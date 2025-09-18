"""Configuration profiles management for network connectivity tools."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from core.config_manager import ConfigManager
from ..core.logging_integration import get_network_logging_manager


class ProfileUseCase(Enum):
    """Profile use cases."""
    HOME = "home"
    ENTERPRISE = "enterprise"
    SECURITY_AUDIT = "security_audit"
    DEVELOPMENT = "development"
    TESTING = "testing"
    CUSTOM = "custom"


@dataclass
class ProfileTemplate:
    """Profile template definition."""
    name: str
    description: str
    use_case: ProfileUseCase
    settings: Dict[str, Any]
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ConfigProfileManager:
    """Manages configuration profiles for network connectivity tools."""
    
    def __init__(self):
        self.logger = get_network_logging_manager().get_tool_logger(
            'ConfigProfileManager'
        )
        self.config_manager = ConfigManager()
        
        # Profile templates
        self._templates: Dict[str, ProfileTemplate] = {}
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize the profile manager."""
        try:
            self._create_default_templates()
            self.logger.info("Configuration profile manager initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize profile manager: {e}")
            raise
    
    def _create_default_templates(self):
        """Create default profile templates."""
        # Home user profile
        home_settings = {
            "general": {
                "default_timeout": 5000,
                "max_concurrent_operations": 5,
                "enable_logging": True,
                "log_level": "INFO",
                "auto_save_results": True,
                "results_retention_days": 7,
                "enable_notifications": True,
                "notification_sound": True
            },
            "bandwidth_monitor": {
                "monitoring_interval": 2000,
                "data_retention_hours": 12,
                "alert_threshold_mbps": 50.0,
                "enable_alerts": True,
                "enable_real_time_chart": True,
                "show_upload_download_separate": True
            },
            "wifi_analyzer": {
                "scan_interval": 60000,
                "signal_interval": 5000,
                "enable_security_analysis": True,
                "enable_interference_detection": False,
                "max_access_points": 100,
                "weak_signal_threshold": -70
            },
            "port_scanner": {
                "default_scan_type": "tcp",
                "common_ports": [21, 22, 23, 25, 53, 80, 443, 993, 995],
                "scan_timeout": 5000,
                "max_threads": 20,
                "enable_service_detection": False,
                "stealth_mode": False
            },
            "security": {
                "security_level": "moderate",
                "enable_scan_logging": True,
                "alert_on_suspicious_activity": True
            },
            "performance": {
                "enable_performance_monitoring": True,
                "max_memory_usage_mb": 256,
                "max_cpu_usage_percent": 50
            }
        }
        
        self._templates["home"] = ProfileTemplate(
            name="Home User",
            description="Optimized for home users with basic monitoring needs",
            use_case=ProfileUseCase.HOME,
            settings=home_settings,
            tags=["default", "basic", "home"]
        )
        
        # Enterprise profile
        enterprise_settings = {
            "general": {
                "default_timeout": 10000,
                "max_concurrent_operations": 20,
                "enable_logging": True,
                "log_level": "DEBUG",
                "auto_save_results": True,
                "results_retention_days": 90,
                "enable_notifications": True,
                "notification_sound": False
            },
            "bandwidth_monitor": {
                "monitoring_interval": 1000,
                "data_retention_hours": 168,  # 1 week
                "alert_threshold_mbps": 500.0,
                "enable_alerts": True,
                "enable_real_time_chart": True,
                "show_upload_download_separate": True,
                "enable_application_monitoring": True,
                "peak_detection_enabled": True,
                "baseline_calculation_hours": 168
            },
            "wifi_analyzer": {
                "scan_interval": 30000,
                "signal_interval": 2000,
                "enable_security_analysis": True,
                "enable_interference_detection": True,
                "enable_channel_analysis": True,
                "max_access_points": 1000,
                "weak_signal_threshold": -75,
                "security_alert_level": "high",
                "vendor_identification": True,
                "hidden_network_detection": True
            },
            "port_scanner": {
                "default_scan_type": "tcp",
                "common_ports": [
                    21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                    443, 993, 995, 1723, 3306, 3389, 5432, 5900,
                    8080, 8443, 9090, 9443
                ],
                "scan_timeout": 3000,
                "max_threads": 100,
                "enable_service_detection": True,
                "enable_os_detection": True,
                "enable_vulnerability_scan": True,
                "stealth_mode": False,
                "enable_banner_grabbing": True
            },
            "security": {
                "security_level": "strict",
                "require_admin_for_scans": True,
                "enable_scan_logging": True,
                "alert_on_suspicious_activity": True,
                "encrypt_stored_data": True,
                "audit_trail_enabled": True
            },
            "performance": {
                "enable_performance_monitoring": True,
                "max_memory_usage_mb": 1024,
                "max_cpu_usage_percent": 75,
                "enable_background_operations": True,
                "cache_size_mb": 128
            }
        }
        
        self._templates["enterprise"] = ProfileTemplate(
            name="Enterprise",
            description="Comprehensive monitoring for enterprise environments",
            use_case=ProfileUseCase.ENTERPRISE,
            settings=enterprise_settings,
            tags=["enterprise", "comprehensive", "business"]
        )
        
        # Security audit profile
        security_settings = {
            "general": {
                "default_timeout": 15000,
                "max_concurrent_operations": 10,
                "enable_logging": True,
                "log_level": "DEBUG",
                "auto_save_results": True,
                "results_retention_days": 365,
                "enable_notifications": True,
                "notification_sound": True
            },
            "bandwidth_monitor": {
                "monitoring_interval": 1000,
                "data_retention_hours": 72,
                "alert_threshold_mbps": 100.0,
                "enable_alerts": True,
                "enable_real_time_chart": True,
                "show_upload_download_separate": True,
                "enable_application_monitoring": True
            },
            "wifi_analyzer": {
                "scan_interval": 15000,
                "signal_interval": 1000,
                "enable_security_analysis": True,
                "enable_interference_detection": True,
                "enable_channel_analysis": True,
                "max_access_points": 1000,
                "weak_signal_threshold": -80,
                "security_alert_level": "high",
                "scan_type": "active",
                "vendor_identification": True,
                "hidden_network_detection": True,
                "beacon_analysis": True,
                "probe_request_analysis": True
            },
            "port_scanner": {
                "default_scan_type": "tcp",
                "common_ports": list(range(1, 1025)),  # All well-known ports
                "scan_timeout": 10000,
                "max_threads": 50,
                "enable_service_detection": True,
                "enable_os_detection": True,
                "enable_vulnerability_scan": True,
                "stealth_mode": True,
                "randomize_scan_order": True,
                "enable_banner_grabbing": True,
                "scan_delay": 100
            },
            "security": {
                "security_level": "strict",
                "require_admin_for_scans": True,
                "enable_scan_logging": True,
                "alert_on_suspicious_activity": True,
                "encrypt_stored_data": True,
                "audit_trail_enabled": True,
                "data_retention_policy": "365_days"
            },
            "performance": {
                "enable_performance_monitoring": True,
                "max_memory_usage_mb": 512,
                "max_cpu_usage_percent": 60,
                "enable_background_operations": True,
                "priority_level": "high"
            }
        }
        
        self._templates["security_audit"] = ProfileTemplate(
            name="Security Audit",
            description="Intensive security scanning and monitoring",
            use_case=ProfileUseCase.SECURITY_AUDIT,
            settings=security_settings,
            tags=["security", "audit", "intensive", "compliance"]
        )
        
        # Development profile
        development_settings = {
            "general": {
                "default_timeout": 3000,
                "max_concurrent_operations": 15,
                "enable_logging": True,
                "log_level": "DEBUG",
                "auto_save_results": False,
                "results_retention_days": 1,
                "enable_notifications": False,
                "notification_sound": False
            },
            "bandwidth_monitor": {
                "monitoring_interval": 5000,
                "data_retention_hours": 2,
                "alert_threshold_mbps": 10.0,
                "enable_alerts": False,
                "enable_real_time_chart": True,
                "show_upload_download_separate": True
            },
            "wifi_analyzer": {
                "scan_interval": 120000,
                "signal_interval": 10000,
                "enable_security_analysis": False,
                "enable_interference_detection": False,
                "max_access_points": 50,
                "weak_signal_threshold": -60
            },
            "port_scanner": {
                "default_scan_type": "tcp",
                "common_ports": [22, 80, 443, 3000, 8000, 8080, 9000],
                "scan_timeout": 2000,
                "max_threads": 10,
                "enable_service_detection": True,
                "stealth_mode": False
            },
            "security": {
                "security_level": "permissive",
                "enable_scan_logging": False,
                "alert_on_suspicious_activity": False
            },
            "performance": {
                "enable_performance_monitoring": False,
                "max_memory_usage_mb": 128,
                "max_cpu_usage_percent": 25
            }
        }
        
        self._templates["development"] = ProfileTemplate(
            name="Development",
            description="Lightweight configuration for development work",
            use_case=ProfileUseCase.DEVELOPMENT,
            settings=development_settings,
            tags=["development", "lightweight", "testing"]
        )
    
    def get_templates(self) -> List[ProfileTemplate]:
        """Get all available profile templates.
        
        Returns:
            List of profile templates
        """
        return list(self._templates.values())
    
    def get_template(self, name: str) -> Optional[ProfileTemplate]:
        """Get a specific profile template.
        
        Args:
            name: Template name
            
        Returns:
            Profile template or None if not found
        """
        return self._templates.get(name)
    
    def get_templates_by_use_case(self, use_case: ProfileUseCase) -> List[ProfileTemplate]:
        """Get templates filtered by use case.
        
        Args:
            use_case: Use case to filter by
            
        Returns:
            List of matching templates
        """
        return [
            template for template in self._templates.values()
            if template.use_case == use_case
        ]
    
    def create_profile_from_template(self, template_name: str, 
                                   profile_name: str = None) -> bool:
        """Create a configuration profile from a template.
        
        Args:
            template_name: Name of the template to use
            profile_name: Name for the new profile (uses template name if None)
            
        Returns:
            True if created successfully
        """
        try:
            template = self._templates.get(template_name)
            if not template:
                self.logger.error(f"Template not found: {template_name}")
                return False
            
            if profile_name is None:
                profile_name = template.name
            
            # Use the configuration service to create the profile
            from ..core.config_service import get_config_service
            
            config_service = get_config_service()
            return config_service.create_profile(
                name=profile_name,
                description=template.description,
                use_case=template.use_case.value,
                settings={"network_connectivity": template.settings},
                tags=template.tags.copy()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create profile from template: {e}")
            return False
    
    def export_template(self, template_name: str, file_path: str) -> bool:
        """Export a template to file.
        
        Args:
            template_name: Name of the template to export
            file_path: Export file path
            
        Returns:
            True if exported successfully
        """
        try:
            template = self._templates.get(template_name)
            if not template:
                self.logger.error(f"Template not found: {template_name}")
                return False
            
            export_data = {
                'template': asdict(template),
                'export_timestamp': datetime.now().isoformat(),
                'export_version': '1.0.0'
            }
            
            # Convert enum to string for JSON serialization
            export_data['template']['use_case'] = template.use_case.value
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported template {template_name} to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export template: {e}")
            return False
    
    def import_template(self, file_path: str, template_name: str = None) -> bool:
        """Import a template from file.
        
        Args:
            file_path: Import file path
            template_name: Name for the imported template (uses file name if None)
            
        Returns:
            True if imported successfully
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'template' not in import_data:
                raise ValueError("Invalid template file: missing template section")
            
            template_data = import_data['template']
            
            # Convert string back to enum
            template_data['use_case'] = ProfileUseCase(template_data['use_case'])
            
            if template_name:
                template_data['name'] = template_name
            
            template = ProfileTemplate(**template_data)
            self._templates[template.name.lower().replace(' ', '_')] = template
            
            self.logger.info(f"Imported template: {template.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import template: {e}")
            return False
    
    def customize_template(self, base_template: str, customizations: Dict[str, Any],
                          new_name: str, description: str = None) -> bool:
        """Create a customized template based on an existing one.
        
        Args:
            base_template: Name of the base template
            customizations: Settings to customize
            new_name: Name for the new template
            description: Description for the new template
            
        Returns:
            True if created successfully
        """
        try:
            base = self._templates.get(base_template)
            if not base:
                self.logger.error(f"Base template not found: {base_template}")
                return False
            
            # Deep copy base settings
            import copy
            new_settings = copy.deepcopy(base.settings)
            
            # Apply customizations
            self._deep_update(new_settings, customizations)
            
            # Create new template
            new_template = ProfileTemplate(
                name=new_name,
                description=description or f"Customized {base.name}",
                use_case=ProfileUseCase.CUSTOM,
                settings=new_settings,
                tags=base.tags + ["custom", "customized"]
            )
            
            template_key = new_name.lower().replace(' ', '_')
            self._templates[template_key] = new_template
            
            self.logger.info(f"Created customized template: {new_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to customize template: {e}")
            return False
    
    def _deep_update(self, base_dict: Dict[str, Any], 
                    update_dict: Dict[str, Any]) -> None:
        """Deep update a dictionary with another dictionary.
        
        Args:
            base_dict: Dictionary to update
            update_dict: Dictionary with updates
        """
        for key, value in update_dict.items():
            if (key in base_dict and 
                isinstance(base_dict[key], dict) and 
                isinstance(value, dict)):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def validate_template_settings(self, settings: Dict[str, Any]) -> List[str]:
        """Validate template settings.
        
        Args:
            settings: Settings to validate
            
        Returns:
            List of validation errors
        """
        try:
            from ..core.config_service import get_config_service
            
            config_service = get_config_service()
            return config_service.validate_configuration(
                {"network_connectivity": settings}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to validate template settings: {e}")
            return [f"Validation error: {e}"]
    
    def get_template_comparison(self, template1: str, 
                               template2: str) -> Dict[str, Any]:
        """Compare two templates and show differences.
        
        Args:
            template1: First template name
            template2: Second template name
            
        Returns:
            Dictionary with comparison results
        """
        try:
            t1 = self._templates.get(template1)
            t2 = self._templates.get(template2)
            
            if not t1 or not t2:
                return {"error": "One or both templates not found"}
            
            differences = self._find_differences(t1.settings, t2.settings)
            
            return {
                "template1": {
                    "name": t1.name,
                    "use_case": t1.use_case.value,
                    "description": t1.description
                },
                "template2": {
                    "name": t2.name,
                    "use_case": t2.use_case.value,
                    "description": t2.description
                },
                "differences": differences,
                "similarity_score": self._calculate_similarity(t1.settings, t2.settings)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to compare templates: {e}")
            return {"error": str(e)}
    
    def _find_differences(self, dict1: Dict[str, Any], 
                         dict2: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
        """Find differences between two dictionaries.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            path: Current path in the dictionary
            
        Returns:
            List of differences
        """
        differences = []
        
        # Check keys in dict1
        for key, value1 in dict1.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in dict2:
                differences.append({
                    "path": current_path,
                    "type": "missing_in_template2",
                    "value1": value1,
                    "value2": None
                })
            elif isinstance(value1, dict) and isinstance(dict2[key], dict):
                differences.extend(
                    self._find_differences(value1, dict2[key], current_path)
                )
            elif value1 != dict2[key]:
                differences.append({
                    "path": current_path,
                    "type": "different_value",
                    "value1": value1,
                    "value2": dict2[key]
                })
        
        # Check keys only in dict2
        for key, value2 in dict2.items():
            if key not in dict1:
                current_path = f"{path}.{key}" if path else key
                differences.append({
                    "path": current_path,
                    "type": "missing_in_template1",
                    "value1": None,
                    "value2": value2
                })
        
        return differences
    
    def _calculate_similarity(self, dict1: Dict[str, Any], 
                             dict2: Dict[str, Any]) -> float:
        """Calculate similarity score between two dictionaries.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Flatten both dictionaries
            flat1 = self._flatten_dict(dict1)
            flat2 = self._flatten_dict(dict2)
            
            # Get all keys
            all_keys = set(flat1.keys()) | set(flat2.keys())
            
            if not all_keys:
                return 1.0
            
            # Count matching values
            matches = 0
            for key in all_keys:
                if key in flat1 and key in flat2 and flat1[key] == flat2[key]:
                    matches += 1
            
            return matches / len(all_keys)
            
        except Exception:
            return 0.0
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', 
                     sep: str = '.') -> Dict[str, Any]:
        """Flatten a nested dictionary.
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def get_recommended_template(self, requirements: Dict[str, Any]) -> Optional[str]:
        """Get recommended template based on requirements.
        
        Args:
            requirements: Dictionary with requirements
            
        Returns:
            Recommended template name or None
        """
        try:
            use_case = requirements.get('use_case')
            environment = requirements.get('environment', 'home')
            security_level = requirements.get('security_level', 'moderate')
            performance_needs = requirements.get('performance_needs', 'basic')
            
            # Simple recommendation logic
            if use_case == 'security' or security_level == 'high':
                return 'security_audit'
            elif environment == 'enterprise' or performance_needs == 'high':
                return 'enterprise'
            elif environment == 'development' or use_case == 'testing':
                return 'development'
            else:
                return 'home'
                
        except Exception as e:
            self.logger.error(f"Failed to get recommendation: {e}")
            return None


# Global instance for easy access
_profile_manager = None


def get_profile_manager() -> ConfigProfileManager:
    """Get global profile manager instance.
    
    Returns:
        ConfigProfileManager instance
    """
    global _profile_manager
    
    if _profile_manager is None:
        _profile_manager = ConfigProfileManager()
    
    return _profile_manager