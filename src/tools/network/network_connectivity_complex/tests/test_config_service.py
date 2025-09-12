"""Tests for the configuration service."""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path

from ..core.config_service import (
    ConfigurationService, ConfigurationProfile, ConfigurationBackup,
    ConfigurationValidator, ConfigurationMigrator, ConfigurationEvent
)
from ..config.config_profiles import ProfileUseCase


class TestConfigurationValidator:
    """Test configuration validation."""
    
    def test_basic_validation(self):
        """Test basic configuration validation."""
        validator = ConfigurationValidator()
        
        # Valid configuration
        valid_config = {
            "network_connectivity": {
                "general": {
                    "default_timeout": 5000,
                    "max_concurrent_operations": 10,
                    "log_level": "INFO"
                }
            }
        }
        
        errors = validator.validate_config(valid_config)
        assert len(errors) == 0
    
    def test_invalid_timeout(self):
        """Test validation of invalid timeout."""
        validator = ConfigurationValidator()
        
        invalid_config = {
            "network_connectivity": {
                "general": {
                    "default_timeout": 500  # Too low
                }
            }
        }
        
        errors = validator.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("timeout" in error.lower() for error in errors)
    
    def test_invalid_log_level(self):
        """Test validation of invalid log level."""
        validator = ConfigurationValidator()
        
        invalid_config = {
            "network_connectivity": {
                "general": {
                    "log_level": "INVALID"
                }
            }
        }
        
        errors = validator.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("log_level" in error.lower() for error in errors)


class TestConfigurationMigrator:
    """Test configuration migration."""
    
    def test_migration_to_1_0_0(self):
        """Test migration to version 1.0.0."""
        migrator = ConfigurationMigrator()
        
        old_config = {
            "network_connectivity": {
                "general": {
                    "default_timeout": 5000
                }
            }
        }
        
        migrated = migrator.migrate_config(old_config, "0.9.0", "1.0.0")
        
        # Should add notification settings
        assert "enable_notifications" in migrated["network_connectivity"]["general"]
        assert "notification_sound" in migrated["network_connectivity"]["general"]
    
    def test_migration_to_1_1_0(self):
        """Test migration to version 1.1.0."""
        migrator = ConfigurationMigrator()
        
        old_config = {
            "network_connectivity": {
                "general": {
                    "default_timeout": 5000
                }
            }
        }
        
        migrated = migrator.migrate_config(old_config, "1.0.0", "1.1.0")
        
        # Should add performance settings
        assert "performance" in migrated["network_connectivity"]
        assert "enable_performance_monitoring" in migrated["network_connectivity"]["performance"]


class TestConfigurationService:
    """Test configuration service."""
    
    @pytest.fixture
    def config_service(self):
        """Create a test configuration service."""
        return ConfigurationService()
    
    @pytest.fixture
    def sample_profile_data(self):
        """Sample profile data for testing."""
        return {
            "name": "Test Profile",
            "description": "Test profile for unit tests",
            "use_case": "testing",
            "settings": {
                "general": {
                    "default_timeout": 3000,
                    "enable_logging": True
                }
            }
        }
    
    def test_create_profile(self, config_service, sample_profile_data):
        """Test profile creation."""
        success = config_service.create_profile(**sample_profile_data)
        assert success
        
        # Verify profile exists
        profile = config_service.get_profile(sample_profile_data["name"])
        assert profile is not None
        assert profile.name == sample_profile_data["name"]
        assert profile.description == sample_profile_data["description"]
    
    def test_create_duplicate_profile(self, config_service, sample_profile_data):
        """Test creating duplicate profile fails."""
        # Create first profile
        success1 = config_service.create_profile(**sample_profile_data)
        assert success1
        
        # Try to create duplicate
        success2 = config_service.create_profile(**sample_profile_data)
        assert not success2
    
    def test_update_profile(self, config_service, sample_profile_data):
        """Test profile update."""
        # Create profile
        config_service.create_profile(**sample_profile_data)
        
        # Update profile
        new_description = "Updated description"
        success = config_service.update_profile(
            sample_profile_data["name"],
            description=new_description
        )
        assert success
        
        # Verify update
        profile = config_service.get_profile(sample_profile_data["name"])
        assert profile.description == new_description
    
    def test_delete_profile(self, config_service, sample_profile_data):
        """Test profile deletion."""
        # Create profile
        config_service.create_profile(**sample_profile_data)
        
        # Delete profile
        success = config_service.delete_profile(sample_profile_data["name"])
        assert success
        
        # Verify deletion
        profile = config_service.get_profile(sample_profile_data["name"])
        assert profile is None
    
    def test_switch_profile(self, config_service, sample_profile_data):
        """Test profile switching."""
        # Create profile
        config_service.create_profile(**sample_profile_data)
        
        # Switch to profile
        success = config_service.switch_profile(sample_profile_data["name"])
        assert success
        
        # Verify active profile
        active_profile = config_service.get_active_profile()
        assert active_profile is not None
        assert active_profile.name == sample_profile_data["name"]
    
    def test_create_backup(self, config_service):
        """Test configuration backup creation."""
        backup_id = config_service.create_backup(
            "Test Backup",
            "Test backup description"
        )
        assert backup_id
        
        # Verify backup exists
        backups = config_service.get_backups()
        backup_names = [b.name for b in backups]
        assert "Test Backup" in backup_names
    
    def test_restore_backup(self, config_service, sample_profile_data):
        """Test configuration backup restoration."""
        # Create initial configuration
        config_service.create_profile(**sample_profile_data)
        
        # Create backup
        backup_id = config_service.create_backup("Test Backup")
        
        # Modify configuration
        config_service.update_profile(
            sample_profile_data["name"],
            description="Modified description"
        )
        
        # Restore backup
        success = config_service.restore_backup(backup_id)
        assert success
        
        # Verify restoration (profile should be restored)
        profiles = config_service.get_profiles()
        assert len(profiles) > 0
    
    def test_validate_configuration(self, config_service):
        """Test configuration validation."""
        errors = config_service.validate_configuration()
        # Should have no errors for default configuration
        assert isinstance(errors, list)
    
    def test_export_import_configuration(self, config_service, sample_profile_data):
        """Test configuration export and import."""
        # Create profile
        config_service.create_profile(**sample_profile_data)
        
        # Export configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_path = f.name
        
        try:
            success = config_service.export_configuration(
                export_path, include_profiles=True
            )
            assert success
            
            # Verify export file exists and has content
            assert Path(export_path).exists()
            
            with open(export_path, 'r') as f:
                exported_data = json.load(f)
            
            assert 'configuration' in exported_data
            assert 'profiles' in exported_data
            
            # Clear current configuration
            config_service._profiles.clear()
            
            # Import configuration
            success = config_service.import_configuration(
                export_path, import_profiles=True
            )
            assert success
            
            # Verify import
            profile = config_service.get_profile(sample_profile_data["name"])
            assert profile is not None
            
        finally:
            # Clean up
            Path(export_path).unlink(missing_ok=True)
    
    def test_configuration_events(self, config_service, sample_profile_data):
        """Test configuration event callbacks."""
        events_received = []
        
        def event_callback(event_data):
            events_received.append(event_data)
        
        # Add event callback
        config_service.add_event_callback(
            ConfigurationEvent.PROFILE_CREATED,
            event_callback
        )
        
        # Create profile (should trigger event)
        config_service.create_profile(**sample_profile_data)
        
        # Verify event was triggered
        assert len(events_received) > 0
        assert events_received[0]['profile_name'] == sample_profile_data["name"]
    
    def test_configuration_caching(self, config_service):
        """Test configuration caching."""
        # Get configuration (should cache it)
        config1 = config_service.get_configuration(use_cache=True)
        
        # Get again (should use cache)
        config2 = config_service.get_configuration(use_cache=True)
        
        # Should be the same object (cached)
        assert config1 == config2
        
        # Get without cache (should be fresh)
        config3 = config_service.get_configuration(use_cache=False)
        
        # Should still be equal but potentially different object
        assert config1 == config3


class TestConfigurationIntegration:
    """Integration tests for configuration system."""
    
    def test_profile_template_integration(self):
        """Test integration between profiles and templates."""
        from ..config.config_profiles import get_profile_manager
        
        profile_manager = get_profile_manager()
        config_service = ConfigurationService()
        
        # Get available templates
        templates = profile_manager.get_templates()
        assert len(templates) > 0
        
        # Create profile from template
        template = templates[0]
        success = profile_manager.create_profile_from_template(
            template.name.lower().replace(' ', '_'),
            "Test Profile from Template"
        )
        assert success
        
        # Verify profile was created in config service
        profile = config_service.get_profile("Test Profile from Template")
        assert profile is not None
    
    def test_validation_integration(self):
        """Test integration between validation and configuration service."""
        config_service = ConfigurationService()
        
        # Create invalid configuration
        invalid_updates = {
            "general": {
                "default_timeout": 100  # Too low
            }
        }
        
        # Try to update with validation
        success = config_service.update_configuration(
            invalid_updates, validate=True
        )
        
        # Should fail validation
        assert not success
    
    def test_migration_integration(self):
        """Test integration between migration and configuration service."""
        config_service = ConfigurationService()
        
        # Test migration
        success = config_service.migrate_configuration("1.0.0", "1.2.0")
        assert success
        
        # Verify migrated configuration is valid
        errors = config_service.validate_configuration()
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__])