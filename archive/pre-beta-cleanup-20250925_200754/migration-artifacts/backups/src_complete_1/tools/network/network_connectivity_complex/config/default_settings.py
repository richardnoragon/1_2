"""Default configuration settings for network connectivity tools."""

import logging
from typing import Dict, Any, List, Optional


def get_default_config() -> Dict[str, Any]:
    """Get default configuration for network connectivity module.
    
    Returns:
        Dictionary with default configuration settings
    """
    return {
        "network_connectivity": {
            "general": {
                "default_timeout": 5000,
                "max_concurrent_operations": 10,
                "enable_logging": True,
                "log_level": "INFO",
                "auto_save_results": True,
                "results_retention_days": 30,
                "enable_notifications": True,
                "notification_sound": True,
                "data_cache_timeout": 30,
                "max_history_entries": 1000
            },
            "bandwidth_monitor": {
                "monitoring_interval": 1000,
                "data_retention_hours": 24,
                "alert_threshold_mbps": 100.0,
                "enable_alerts": True,
                "monitor_interfaces": "auto",
                "chart_update_interval": 2000,
                "enable_real_time_chart": True,
                "show_upload_download_separate": True,
                "data_units": "auto",
                "enable_application_monitoring": False,
                "alert_email": "",
                "peak_detection_enabled": True,
                "baseline_calculation_hours": 168,
                "export_format": "csv",
                "auto_export_enabled": False,
                "auto_export_interval_hours": 24
            },
            "wifi_analyzer": {
                "scan_interval": 30000,
                "signal_interval": 2000,
                "enable_security_analysis": True,
                "enable_interference_detection": True,
                "enable_channel_analysis": True,
                "data_retention_hours": 24,
                "max_access_points": 1000,
                "enable_alerts": True,
                "weak_signal_threshold": -70,
                "security_alert_level": "medium",
                "scan_type": "active",
                "bands": ["2.4GHz", "5GHz"],
                "channel_width_detection": True,
                "vendor_identification": True,
                "hidden_network_detection": True,
                "beacon_analysis": True,
                "probe_request_analysis": False,
                "monitor_mode_required": False,
                "auto_channel_recommendation": True,
                "interference_threshold": 0.7,
                "security_score_threshold": 0.5,
                "signal_history_size": 1000,
                "export_format": "json",
                "include_vendor_info": True,
                "include_capabilities": True,
                "real_time_updates": True,
                "update_interval": 5000
            },
            "lan_file_transfer": {
                "discovery_port": 8765,
                "transfer_port": 8766,
                "discovery_interval": 30,
                "max_concurrent_transfers": 3,
                "default_chunk_size": 65536,
                "encryption_enabled": True,
                "compression_enabled": False,
                "default_compression": "gzip",
                "transfer_timeout": 300,
                "connection_timeout": 30,
                "enable_device_discovery": True,
                "auto_accept_trusted": False,
                "require_authentication": True,
                "enable_resume": True,
                "max_file_size_mb": 1024,
                "allowed_file_types": [],
                "blocked_file_types": [".exe", ".bat", ".cmd", ".scr"],
                "default_download_path": "Downloads",
                "enable_bandwidth_limiting": False,
                "max_upload_speed_mbps": 0,
                "max_download_speed_mbps": 0,
                "enable_notifications": True,
                "log_transfers": True,
                "keep_transfer_history": True,
                "history_retention_days": 30,
                "enable_security_scanning": False,
                "trust_local_network": True,
                "device_name": "",
                "enable_upnp": False,
                "firewall_auto_config": False
            },
            "connectivity_tester": {
                "default_ping_count": 4,
                "default_ping_size": 32,
                "default_ping_interval": 1000,
                "default_hosts": [
                    "8.8.8.8",
                    "1.1.1.1",
                    "google.com",
                    "cloudflare.com"
                ],
                "traceroute_max_hops": 30,
                "traceroute_timeout": 5000,
                "dns_servers": [
                    "8.8.8.8",
                    "1.1.1.1",
                    "208.67.222.222"
                ],
                "http_test_urls": [
                    "https://www.google.com",
                    "https://www.cloudflare.com",
                    "https://httpbin.org/get"
                ],
                "enable_ipv6_testing": True,
                "save_ping_history": True,
                "alert_on_failure": True,
                "failure_threshold": 3
            },
            "port_scanner": {
                "default_scan_type": "tcp",
                "common_ports": [
                    21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                    443, 993, 995, 1723, 3306, 3389, 5432, 5900
                ],
                "scan_timeout": 3000,
                "max_threads": 50,
                "enable_service_detection": True,
                "enable_os_detection": False,
                "enable_vulnerability_scan": False,
                "scan_delay": 0,
                "randomize_scan_order": False,
                "save_scan_results": True,
                "export_formats": ["json", "csv", "xml"],
                "stealth_mode": False,
                "custom_port_ranges": [],
                "exclude_ports": [],
                "enable_banner_grabbing": True
            },
            "network_diagnostics": {
                "include_system_info": True,
                "include_network_config": True,
                "include_route_table": True,
                "include_dns_config": True,
                "include_firewall_status": True,
                "include_active_connections": True,
                "include_network_adapters": True,
                "include_wireless_info": True,
                "generate_recommendations": True,
                "auto_fix_suggestions": False,
                "detailed_analysis": True,
                "include_performance_metrics": True,
                "save_diagnostic_reports": True,
                "report_format": "html",
                "include_screenshots": False,
                "anonymize_sensitive_data": True
            },
            "security": {
                "require_admin_for_scans": False,
                "whitelist_scan_targets": [],
                "blacklist_scan_targets": [
                    "127.0.0.1",
                    "localhost",
                    "::1"
                ],
                "max_scan_rate": 1000,
                "enable_scan_logging": True,
                "alert_on_suspicious_activity": True,
                "encrypt_stored_data": False,
                "data_retention_policy": "30_days",
                "audit_trail_enabled": True,
                "security_level": "moderate"
            },
            "performance": {
                "enable_performance_monitoring": True,
                "max_memory_usage_mb": 512,
                "max_cpu_usage_percent": 25,
                "operation_timeout_multiplier": 1.0,
                "enable_background_operations": True,
                "priority_level": "normal",
                "thread_pool_size": "auto",
                "cache_size_mb": 64,
                "enable_compression": True
            }
        }
    }


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate network connectivity configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if "network_connectivity" not in config:
        errors.append("Missing 'network_connectivity' section")
        return errors
    
    nc_config = config["network_connectivity"]
    
    # Validate general settings
    if "general" in nc_config:
        general = nc_config["general"]
        
        if "default_timeout" in general:
            timeout = general["default_timeout"]
            if not isinstance(timeout, int) or timeout < 1000 or timeout > 60000:
                errors.append(
                    "default_timeout must be integer between 1000 and 60000"
                )
        
        if "max_concurrent_operations" in general:
            max_ops = general["max_concurrent_operations"]
            if not isinstance(max_ops, int) or max_ops < 1 or max_ops > 100:
                errors.append(
                    "max_concurrent_operations must be integer between 1 and 100"
                )
        
        if "log_level" in general:
            log_level = general["log_level"]
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if log_level not in valid_levels:
                errors.append(
                    f"log_level must be one of: {', '.join(valid_levels)}"
                )
    
    # Validate bandwidth monitor settings
    if "bandwidth_monitor" in nc_config:
        bm = nc_config["bandwidth_monitor"]
        
        if "monitoring_interval" in bm:
            interval = bm["monitoring_interval"]
            if not isinstance(interval, int) or interval < 100 or interval > 10000:
                errors.append(
                    "monitoring_interval must be integer between 100 and 10000"
                )
        
        if "alert_threshold_mbps" in bm:
            threshold = bm["alert_threshold_mbps"]
            if not isinstance(threshold, (int, float)) or threshold < 0.1:
                errors.append(
                    "alert_threshold_mbps must be number >= 0.1"
                )
        
        if "data_retention_hours" in bm:
            retention = bm["data_retention_hours"]
            if not isinstance(retention, int) or retention < 1 or retention > 8760:
                errors.append(
                    "data_retention_hours must be integer between 1 and 8760"
                )
    
    # Validate connectivity tester settings
    if "connectivity_tester" in nc_config:
        ct = nc_config["connectivity_tester"]
        
        if "default_ping_count" in ct:
            count = ct["default_ping_count"]
            if not isinstance(count, int) or count < 1 or count > 100:
                errors.append(
                    "default_ping_count must be integer between 1 and 100"
                )
        
        if "default_ping_size" in ct:
            size = ct["default_ping_size"]
            if not isinstance(size, int) or size < 8 or size > 65507:
                errors.append(
                    "default_ping_size must be integer between 8 and 65507"
                )
        
        if "traceroute_max_hops" in ct:
            hops = ct["traceroute_max_hops"]
            if not isinstance(hops, int) or hops < 1 or hops > 255:
                errors.append(
                    "traceroute_max_hops must be integer between 1 and 255"
                )
    
    # Validate port scanner settings
    if "port_scanner" in nc_config:
        ps = nc_config["port_scanner"]
        
        if "scan_timeout" in ps:
            timeout = ps["scan_timeout"]
            if not isinstance(timeout, int) or timeout < 100 or timeout > 30000:
                errors.append(
                    "scan_timeout must be integer between 100 and 30000"
                )
        
        if "max_threads" in ps:
            threads = ps["max_threads"]
            if not isinstance(threads, int) or threads < 1 or threads > 1000:
                errors.append(
                    "max_threads must be integer between 1 and 1000"
                )
        
        if "common_ports" in ps:
            ports = ps["common_ports"]
            if not isinstance(ports, list):
                errors.append("common_ports must be a list")
            else:
                for port in ports:
                    if not isinstance(port, int) or port < 1 or port > 65535:
                        errors.append(
                            f"Invalid port {port}: must be integer between 1 and 65535"
                        )
                        break
    
    # Validate security settings
    if "security" in nc_config:
        security = nc_config["security"]
        
        if "security_level" in security:
            level = security["security_level"]
            valid_levels = ["strict", "moderate", "permissive"]
            if level not in valid_levels:
                errors.append(
                    f"security_level must be one of: {', '.join(valid_levels)}"
                )
        
        if "max_scan_rate" in security:
            rate = security["max_scan_rate"]
            if not isinstance(rate, int) or rate < 1 or rate > 10000:
                errors.append(
                    "max_scan_rate must be integer between 1 and 10000"
                )
    
    # Validate performance settings
    if "performance" in nc_config:
        perf = nc_config["performance"]
        
        if "max_memory_usage_mb" in perf:
            memory = perf["max_memory_usage_mb"]
            if not isinstance(memory, int) or memory < 64 or memory > 4096:
                errors.append(
                    "max_memory_usage_mb must be integer between 64 and 4096"
                )
        
        if "max_cpu_usage_percent" in perf:
            cpu = perf["max_cpu_usage_percent"]
            if not isinstance(cpu, (int, float)) or cpu < 1 or cpu > 100:
                errors.append(
                    "max_cpu_usage_percent must be number between 1 and 100"
                )
    
    return errors


def get_config_schema() -> Dict[str, Any]:
    """Get configuration schema for validation.
    
    Returns:
        Dictionary describing configuration schema
    """
    return {
        "type": "object",
        "properties": {
            "network_connectivity": {
                "type": "object",
                "properties": {
                    "general": {
                        "type": "object",
                        "properties": {
                            "default_timeout": {
                                "type": "integer",
                                "minimum": 1000,
                                "maximum": 60000
                            },
                            "max_concurrent_operations": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100
                            },
                            "enable_logging": {"type": "boolean"},
                            "log_level": {
                                "type": "string",
                                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                            },
                            "auto_save_results": {"type": "boolean"},
                            "results_retention_days": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 365
                            }
                        }
                    },
                    "bandwidth_monitor": {
                        "type": "object",
                        "properties": {
                            "monitoring_interval": {
                                "type": "integer",
                                "minimum": 100,
                                "maximum": 10000
                            },
                            "alert_threshold_mbps": {
                                "type": "number",
                                "minimum": 0.1
                            },
                            "data_retention_hours": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 8760
                            },
                            "enable_alerts": {"type": "boolean"}
                        }
                    }
                }
            }
        },
        "required": ["network_connectivity"]
    }


def merge_config(base_config: Dict[str, Any], 
                user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user configuration with base configuration.
    
    Args:
        base_config: Base configuration dictionary
        user_config: User configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    def deep_merge(base: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge dictionaries."""
        result = base.copy()
        
        for key, value in user.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    return deep_merge(base_config, user_config)


def get_tool_specific_config(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get default configuration for a specific tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool-specific configuration or None if not found
    """
    default_config = get_default_config()
    nc_config = default_config.get("network_connectivity", {})
    
    return nc_config.get(tool_name)


def create_minimal_config() -> Dict[str, Any]:
    """Create minimal configuration with essential settings only.
    
    Returns:
        Minimal configuration dictionary
    """
    return {
        "network_connectivity": {
            "general": {
                "default_timeout": 5000,
                "enable_logging": True,
                "log_level": "INFO"
            },
            "bandwidth_monitor": {
                "monitoring_interval": 1000,
                "enable_alerts": True,
                "alert_threshold_mbps": 100.0
            }
        }
    }