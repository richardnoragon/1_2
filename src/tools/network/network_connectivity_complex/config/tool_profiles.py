"""Tool profiles and presets for network connectivity tools."""

from typing import Dict, Any, List, Optional


def get_tool_profiles() -> Dict[str, Dict[str, Any]]:
    """Get predefined tool profiles for different use cases.

    Returns:
        Dictionary of tool profiles
    """
    return {
        "bandwidth_monitor": {
            "home_user": {
                "name": "Home User",
                "description": "Basic bandwidth monitoring for home networks",
                "settings": {
                    "monitoring_interval": 2000,
                    "data_retention_hours": 12,
                    "alert_threshold_mbps": 50.0,
                    "enable_alerts": True,
                    "enable_real_time_chart": True,
                    "show_upload_download_separate": True,
                    "auto_export_enabled": False,
                },
            },
            "small_business": {
                "name": "Small Business",
                "description": "Enhanced monitoring for small business networks",
                "settings": {
                    "monitoring_interval": 1000,
                    "data_retention_hours": 48,
                    "alert_threshold_mbps": 100.0,
                    "enable_alerts": True,
                    "enable_real_time_chart": True,
                    "show_upload_download_separate": True,
                    "auto_export_enabled": True,
                    "auto_export_interval_hours": 24,
                    "peak_detection_enabled": True,
                },
            },
            "enterprise": {
                "name": "Enterprise",
                "description": "Comprehensive monitoring for enterprise networks",
                "settings": {
                    "monitoring_interval": 500,
                    "data_retention_hours": 168,
                    "alert_threshold_mbps": 500.0,
                    "enable_alerts": True,
                    "enable_real_time_chart": True,
                    "show_upload_download_separate": True,
                    "auto_export_enabled": True,
                    "auto_export_interval_hours": 12,
                    "peak_detection_enabled": True,
                    "baseline_calculation_hours": 168,
                    "enable_application_monitoring": True,
                },
            },
            "gaming": {
                "name": "Gaming Optimized",
                "description": "Optimized for gaming and low-latency applications",
                "settings": {
                    "monitoring_interval": 500,
                    "data_retention_hours": 24,
                    "alert_threshold_mbps": 25.0,
                    "enable_alerts": True,
                    "enable_real_time_chart": True,
                    "show_upload_download_separate": True,
                    "peak_detection_enabled": True,
                },
            },
            "streaming": {
                "name": "Streaming Media",
                "description": "Optimized for streaming and content delivery",
                "settings": {
                    "monitoring_interval": 1000,
                    "data_retention_hours": 72,
                    "alert_threshold_mbps": 25.0,
                    "enable_alerts": True,
                    "enable_real_time_chart": True,
                    "show_upload_download_separate": True,
                    "peak_detection_enabled": True,
                    "baseline_calculation_hours": 72,
                },
            },
        },
        "connectivity_tester": {
            "basic": {
                "name": "Basic Connectivity",
                "description": "Simple connectivity testing",
                "settings": {
                    "default_ping_count": 4,
                    "default_ping_size": 32,
                    "default_hosts": ["8.8.8.8", "1.1.1.1"],
                    "enable_ipv6_testing": False,
                    "save_ping_history": True,
                    "alert_on_failure": False,
                },
            },
            "comprehensive": {
                "name": "Comprehensive Testing",
                "description": "Thorough connectivity and performance testing",
                "settings": {
                    "default_ping_count": 10,
                    "default_ping_size": 64,
                    "default_hosts": [
                        "8.8.8.8",
                        "1.1.1.1",
                        "208.67.222.222",
                        "google.com",
                        "cloudflare.com",
                    ],
                    "enable_ipv6_testing": True,
                    "save_ping_history": True,
                    "alert_on_failure": True,
                    "failure_threshold": 2,
                    "traceroute_max_hops": 30,
                },
            },
            "troubleshooting": {
                "name": "Network Troubleshooting",
                "description": "Detailed testing for network issue diagnosis",
                "settings": {
                    "default_ping_count": 20,
                    "default_ping_size": 1472,
                    "default_hosts": [
                        "8.8.8.8",
                        "1.1.1.1",
                        "208.67.222.222",
                        "google.com",
                        "cloudflare.com",
                        "github.com",
                    ],
                    "enable_ipv6_testing": True,
                    "save_ping_history": True,
                    "alert_on_failure": True,
                    "failure_threshold": 1,
                    "traceroute_max_hops": 50,
                    "traceroute_timeout": 10000,
                },
            },
        },
        "port_scanner": {
            "security_audit": {
                "name": "Security Audit",
                "description": "Comprehensive security scanning with vulnerability assessment",
                "settings": {
                    "scan_timeout": 5000,
                    "max_threads": 100,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": True,
                    "save_scan_results": True,
                    "scan_policy": "normal",
                    "scan_type": "tcp_connect",
                    "enable_banner_grabbing": True,
                    "security_level": "moderate",
                },
            },
            "quick_scan": {
                "name": "Quick Scan",
                "description": "Fast scanning of common ports",
                "settings": {
                    "scan_timeout": 1000,
                    "max_threads": 50,
                    "enable_service_detection": False,
                    "enable_vulnerability_scan": False,
                    "save_scan_results": True,
                    "scan_policy": "aggressive",
                    "scan_type": "tcp_connect",
                    "common_ports": [
                        21,
                        22,
                        23,
                        25,
                        53,
                        80,
                        443,
                        993,
                        995,
                        3389,
                    ],
                },
            },
            "stealth_scan": {
                "name": "Stealth Scan",
                "description": "Low-profile scanning to avoid detection",
                "settings": {
                    "scan_timeout": 10000,
                    "max_threads": 5,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": False,
                    "save_scan_results": True,
                    "scan_policy": "stealth",
                    "scan_type": "tcp_connect",
                    "scan_delay": 1000,
                    "randomize_scan_order": True,
                    "security_level": "strict",
                },
            },
            "comprehensive": {
                "name": "Comprehensive Scan",
                "description": "Thorough scanning with full service detection",
                "settings": {
                    "scan_timeout": 8000,
                    "max_threads": 25,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": True,
                    "save_scan_results": True,
                    "scan_policy": "polite",
                    "scan_type": "tcp_connect",
                    "enable_banner_grabbing": True,
                    "security_level": "moderate",
                    "scan_delay": 100,
                },
            },
            "udp_scan": {
                "name": "UDP Service Scan",
                "description": "UDP port scanning for service discovery",
                "settings": {
                    "scan_timeout": 5000,
                    "max_threads": 20,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": False,
                    "save_scan_results": True,
                    "scan_policy": "normal",
                    "scan_type": "udp",
                    "common_ports": [
                        53,
                        67,
                        68,
                        69,
                        123,
                        161,
                        162,
                        514,
                        1194,
                        1701,
                    ],
                },
            },
            "web_services": {
                "name": "Web Services Scan",
                "description": "Focused scanning of web-related ports",
                "settings": {
                    "scan_timeout": 3000,
                    "max_threads": 30,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": True,
                    "save_scan_results": True,
                    "scan_policy": "normal",
                    "scan_type": "tcp_connect",
                    "enable_banner_grabbing": True,
                    "common_ports": [
                        80,
                        443,
                        8080,
                        8443,
                        8000,
                        8888,
                        9000,
                        9090,
                        3000,
                        5000,
                    ],
                },
            },
            "database_scan": {
                "name": "Database Services Scan",
                "description": "Scanning for database services",
                "settings": {
                    "scan_timeout": 4000,
                    "max_threads": 15,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": True,
                    "save_scan_results": True,
                    "scan_policy": "polite",
                    "scan_type": "tcp_connect",
                    "enable_banner_grabbing": True,
                    "common_ports": [
                        1433,
                        1521,
                        3306,
                        5432,
                        6379,
                        27017,
                        9042,
                        7000,
                        7001,
                    ],
                },
            },
            "remote_access": {
                "name": "Remote Access Scan",
                "description": "Scanning for remote access services",
                "settings": {
                    "scan_timeout": 3000,
                    "max_threads": 20,
                    "enable_service_detection": True,
                    "enable_vulnerability_scan": True,
                    "save_scan_results": True,
                    "scan_policy": "normal",
                    "scan_type": "tcp_connect",
                    "enable_banner_grabbing": True,
                    "security_level": "strict",
                    "common_ports": [
                        22,
                        23,
                        3389,
                        5900,
                        5901,
                        5902,
                        1723,
                        1701,
                        500,
                        4500,
                    ],
                },
            },
        },
        "network_diagnostics": {
            "basic": {
                "name": "Basic Diagnostics",
                "description": "Essential network information",
                "settings": {
                    "include_system_info": True,
                    "include_network_config": True,
                    "include_route_table": False,
                    "include_dns_config": True,
                    "include_firewall_status": False,
                    "generate_recommendations": True,
                    "detailed_analysis": False,
                },
            },
            "comprehensive": {
                "name": "Comprehensive Diagnostics",
                "description": "Complete network analysis",
                "settings": {
                    "include_system_info": True,
                    "include_network_config": True,
                    "include_route_table": True,
                    "include_dns_config": True,
                    "include_firewall_status": True,
                    "include_active_connections": True,
                    "include_network_adapters": True,
                    "include_wireless_info": True,
                    "generate_recommendations": True,
                    "detailed_analysis": True,
                    "include_performance_metrics": True,
                },
            },
            "troubleshooting": {
                "name": "Troubleshooting Focus",
                "description": "Focused on identifying network issues",
                "settings": {
                    "include_system_info": True,
                    "include_network_config": True,
                    "include_route_table": True,
                    "include_dns_config": True,
                    "include_firewall_status": True,
                    "include_active_connections": True,
                    "generate_recommendations": True,
                    "auto_fix_suggestions": True,
                    "detailed_analysis": True,
                    "anonymize_sensitive_data": False,
                },
            },
        },
    }


def create_custom_profile(
    tool_name: str,
    profile_name: str,
    description: str,
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a custom tool profile.

    Args:
        tool_name: Name of the tool
        profile_name: Name of the profile
        description: Profile description
        settings: Profile settings

    Returns:
        Custom profile dictionary
    """
    return {
        "name": profile_name,
        "description": description,
        "settings": settings,
        "custom": True,
        "tool": tool_name,
    }


def get_profile_by_name(
    tool_name: str, profile_name: str
) -> Optional[Dict[str, Any]]:
    """Get a specific profile by tool and profile name.

    Args:
        tool_name: Name of the tool
        profile_name: Name of the profile

    Returns:
        Profile dictionary or None if not found
    """
    profiles = get_tool_profiles()

    if tool_name in profiles and profile_name in profiles[tool_name]:
        return profiles[tool_name][profile_name]

    return None


def list_profiles_for_tool(tool_name: str) -> List[str]:
    """List available profiles for a tool.

    Args:
        tool_name: Name of the tool

    Returns:
        List of profile names
    """
    profiles = get_tool_profiles()

    if tool_name in profiles:
        return list(profiles[tool_name].keys())

    return []


def get_profile_settings(
    tool_name: str, profile_name: str
) -> Optional[Dict[str, Any]]:
    """Get settings for a specific profile.

    Args:
        tool_name: Name of the tool
        profile_name: Name of the profile

    Returns:
        Profile settings or None if not found
    """
    profile = get_profile_by_name(tool_name, profile_name)

    if profile:
        return profile.get("settings", {})

    return None


def validate_profile_settings(
    tool_name: str, settings: Dict[str, Any]
) -> List[str]:
    """Validate profile settings for a tool.

    Args:
        tool_name: Name of the tool
        settings: Settings to validate

    Returns:
        List of validation errors
    """
    errors = []

    # Tool-specific validation
    if tool_name == "bandwidth_monitor":
        if "monitoring_interval" in settings:
            interval = settings["monitoring_interval"]
            if not isinstance(interval, int) or interval < 100:
                errors.append("monitoring_interval must be integer >= 100")

        if "alert_threshold_mbps" in settings:
            threshold = settings["alert_threshold_mbps"]
            if not isinstance(threshold, (int, float)) or threshold <= 0:
                errors.append("alert_threshold_mbps must be positive number")

    elif tool_name == "connectivity_tester":
        if "default_ping_count" in settings:
            count = settings["default_ping_count"]
            if not isinstance(count, int) or count < 1 or count > 100:
                errors.append("default_ping_count must be integer 1-100")

        if "default_hosts" in settings:
            hosts = settings["default_hosts"]
            if not isinstance(hosts, list) or len(hosts) == 0:
                errors.append("default_hosts must be non-empty list")

    elif tool_name == "port_scanner":
        if "max_threads" in settings:
            threads = settings["max_threads"]
            if not isinstance(threads, int) or threads < 1 or threads > 1000:
                errors.append("max_threads must be integer 1-1000")

        if "scan_timeout" in settings:
            timeout = settings["scan_timeout"]
            if not isinstance(timeout, int) or timeout < 100:
                errors.append("scan_timeout must be integer >= 100")

    return errors


def merge_profile_with_defaults(
    tool_name: str,
    profile_settings: Dict[str, Any],
    default_settings: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge profile settings with default settings.

    Args:
        tool_name: Name of the tool
        profile_settings: Profile-specific settings
        default_settings: Default tool settings

    Returns:
        Merged settings dictionary
    """
    merged = default_settings.copy()
    merged.update(profile_settings)
    return merged


def export_profile(
    tool_name: str, profile_name: str
) -> Optional[Dict[str, Any]]:
    """Export a profile for sharing or backup.

    Args:
        tool_name: Name of the tool
        profile_name: Name of the profile

    Returns:
        Exportable profile dictionary
    """
    profile = get_profile_by_name(tool_name, profile_name)

    if profile:
        return {
            "tool_name": tool_name,
            "profile_name": profile_name,
            "profile_data": profile,
            "export_version": "1.0",
        }

    return None


def import_profile(profile_data: Dict[str, Any]) -> bool:
    """Import a profile from exported data.

    Args:
        profile_data: Exported profile data

    Returns:
        True if import successful
    """
    try:
        required_keys = ["tool_name", "profile_name", "profile_data"]
        if not all(key in profile_data for key in required_keys):
            return False

        tool_name = profile_data["tool_name"]
        profile_name = profile_data["profile_name"]
        profile = profile_data["profile_data"]

        # Validate profile structure
        if not isinstance(profile, dict) or "settings" not in profile:
            return False

        # Validate settings
        errors = validate_profile_settings(tool_name, profile["settings"])
        if errors:
            return False

        # Import would be handled by the configuration manager
        return True

    except Exception:
        return False
