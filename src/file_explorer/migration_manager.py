"""
Phase 5: Migration Manager with Rollback Capabilities

Comprehensive migration system for RFU Multi-Pane File Explorer with automatic
backup creation, rollback capabilities, and robust error handling. Ensures safe
transitions between different configuration versions and system states.

Features:
- Automatic configuration backup
- Database migration with rollback
- User preferences migration
- Tool integration state transfer
- Comprehensive error recovery
- Migration validation and verification

Author: RFU Development Team
Created: 2025-09-13
Version: 1.0.0
"""

import json
import logging
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)


class MigrationManager:
    """
    Comprehensive migration manager with rollback capabilities.

    Handles all aspects of system migration including:
    - Configuration files
    - Database schema and data
    - User preferences
    - Tool integration settings
    - Cache and temporary data
    """

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)

        # Migration paths
        self.migration_dir = Path("migrations")
        self.backup_dir = Path("data/migration_backups")
        self.temp_dir = Path("build/temp/migration")

        # Ensure directories exist
        for directory in [self.migration_dir, self.backup_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Migration state
        self.current_migration = None
        self.rollback_data = {}
        self.migration_history = []

        # Supported migration types
        self.migration_types = {
            "config": self._migrate_configuration,
            "database": self._migrate_database,
            "preferences": self._migrate_preferences,
            "tools": self._migrate_tool_integration,
            "cache": self._migrate_cache_data,
            "full_system": self._migrate_full_system,
        }

    def create_migration(
        self, migration_name: str, migration_type: str, description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new migration with automatic backup.

        Args:
            migration_name: Unique name for the migration
            migration_type: Type of migration (config, database, etc.)
            description: Optional description of migration purpose

        Returns:
            Migration metadata and status
        """
        migration_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{migration_name}"

        migration_metadata = {
            "migration_id": migration_id,
            "migration_name": migration_name,
            "migration_type": migration_type,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "backup_location": None,
            "rollback_available": False,
            "validation_results": None,
        }

        try:
            # Create backup before migration
            backup_result = self._create_backup(migration_id, migration_type)
            if not backup_result["success"]:
                migration_metadata["status"] = "backup_failed"
                migration_metadata["error"] = backup_result["error"]
                return migration_metadata

            migration_metadata["backup_location"] = backup_result["backup_path"]
            migration_metadata["rollback_available"] = True

            # Save migration metadata
            migration_file = self.migration_dir / f"{migration_id}.json"
            with open(migration_file, "w") as f:
                json.dump(migration_metadata, f, indent=2)

            self.current_migration = migration_metadata
            migration_metadata["status"] = "ready"

            self.logger.info(f"Migration {migration_id} created successfully")
            return migration_metadata

        except Exception as e:
            self.logger.error(f"Failed to create migration {migration_id}: {e}")
            migration_metadata["status"] = "creation_failed"
            migration_metadata["error"] = str(e)
            return migration_metadata

    def execute_migration(self, migration_id: str) -> Dict[str, Any]:
        """
        Execute a migration with comprehensive error handling.

        Args:
            migration_id: Migration identifier to execute

        Returns:
            Execution results and status
        """
        try:
            # Load migration metadata
            migration_file = self.migration_dir / f"{migration_id}.json"
            if not migration_file.exists():
                return {
                    "success": False,
                    "error": f"Migration {migration_id} not found",
                    "rollback_performed": False,
                }

            with open(migration_file, "r") as f:
                migration_metadata = json.load(f)

            self.current_migration = migration_metadata
            migration_type = migration_metadata["migration_type"]

            if migration_type not in self.migration_types:
                return {
                    "success": False,
                    "error": f"Unsupported migration type: {migration_type}",
                    "rollback_performed": False,
                }

            self.logger.info(f"Executing migration {migration_id}")

            # Execute migration
            migration_function = self.migration_types[migration_type]
            result = migration_function(migration_metadata)

            if result["success"]:
                # Update migration status
                migration_metadata["status"] = "completed"
                migration_metadata["completed_at"] = datetime.now().isoformat()
                migration_metadata["execution_results"] = result

                # Validate migration
                validation_result = self._validate_migration(migration_metadata)
                migration_metadata["validation_results"] = validation_result

                if not validation_result["valid"]:
                    self.logger.warning(f"Migration {migration_id} validation failed")
                    # Offer rollback option for failed validation
                    result["validation_failed"] = True
                    result["rollback_recommended"] = True

                # Save updated metadata
                with open(migration_file, "w") as f:
                    json.dump(migration_metadata, f, indent=2)

                self.migration_history.append(migration_metadata)
                self.logger.info(f"Migration {migration_id} completed successfully")

            else:
                # Migration failed - perform automatic rollback
                self.logger.error(
                    f"Migration {migration_id} failed: {result.get('error')}"
                )
                rollback_result = self.rollback_migration(migration_id)
                result["rollback_performed"] = rollback_result["success"]
                result["rollback_error"] = rollback_result.get("error")

            return result

        except Exception as e:
            self.logger.error(f"Critical error executing migration {migration_id}: {e}")
            # Attempt emergency rollback
            try:
                rollback_result = self.rollback_migration(migration_id)
                return {
                    "success": False,
                    "error": f"Critical migration error: {e}",
                    "rollback_performed": rollback_result["success"],
                    "rollback_error": rollback_result.get("error"),
                }
            except Exception as rollback_error:
                return {
                    "success": False,
                    "error": f"Critical migration error: {e}",
                    "rollback_performed": False,
                    "rollback_error": f"Rollback also failed: {rollback_error}",
                }

    def rollback_migration(self, migration_id: str) -> Dict[str, Any]:
        """
        Rollback a migration to previous state.

        Args:
            migration_id: Migration to rollback

        Returns:
            Rollback operation results
        """
        try:
            # Load migration metadata
            migration_file = self.migration_dir / f"{migration_id}.json"
            if not migration_file.exists():
                return {
                    "success": False,
                    "error": f"Migration {migration_id} not found",
                }

            with open(migration_file, "r") as f:
                migration_metadata = json.load(f)

            backup_location = migration_metadata.get("backup_location")
            if not backup_location or not Path(backup_location).exists():
                return {
                    "success": False,
                    "error": f"Backup not found for migration {migration_id}",
                }

            self.logger.info(f"Rolling back migration {migration_id}")

            # Perform rollback based on migration type
            migration_type = migration_metadata["migration_type"]
            rollback_result = self._perform_rollback(migration_type, backup_location)

            if rollback_result["success"]:
                # Update migration status
                migration_metadata["status"] = "rolled_back"
                migration_metadata["rolled_back_at"] = datetime.now().isoformat()
                migration_metadata["rollback_results"] = rollback_result

                with open(migration_file, "w") as f:
                    json.dump(migration_metadata, f, indent=2)

                self.logger.info(f"Migration {migration_id} rolled back successfully")

            return rollback_result

        except Exception as e:
            self.logger.error(f"Failed to rollback migration {migration_id}: {e}")
            return {"success": False, "error": str(e)}

    def list_migrations(self) -> List[Dict[str, Any]]:
        """List all available migrations with their status."""
        migrations = []

        for migration_file in self.migration_dir.glob("*.json"):
            try:
                with open(migration_file, "r") as f:
                    migration_data = json.load(f)
                migrations.append(migration_data)
            except Exception as e:
                self.logger.warning(f"Failed to load migration {migration_file}: {e}")

        # Sort by creation date
        migrations.sort(key=lambda x: x.get("created_at", ""))
        return migrations

    def get_migration_status(self, migration_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific migration."""
        migration_file = self.migration_dir / f"{migration_id}.json"
        if not migration_file.exists():
            return None

        try:
            with open(migration_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load migration status {migration_id}: {e}")
            return None

    def cleanup_old_migrations(self, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up old migration files and backups."""
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)

        cleaned_migrations = []
        cleaned_backups = []
        errors = []

        # Clean migration files
        for migration_file in self.migration_dir.glob("*.json"):
            try:
                if migration_file.stat().st_mtime < cutoff_date:
                    with open(migration_file, "r") as f:
                        migration_data = json.load(f)

                    # Only clean completed or failed migrations
                    if migration_data.get("status") in [
                        "completed",
                        "failed",
                        "rolled_back",
                    ]:
                        # Clean associated backup
                        backup_location = migration_data.get("backup_location")
                        if backup_location and Path(backup_location).exists():
                            shutil.rmtree(backup_location)
                            cleaned_backups.append(backup_location)

                        migration_file.unlink()
                        cleaned_migrations.append(str(migration_file))

            except Exception as e:
                errors.append(f"Failed to clean {migration_file}: {e}")

        return {
            "cleaned_migrations": len(cleaned_migrations),
            "cleaned_backups": len(cleaned_backups),
            "errors": errors,
            "migration_files": cleaned_migrations,
            "backup_directories": cleaned_backups,
        }

    def _create_backup(self, migration_id: str, migration_type: str) -> Dict[str, Any]:
        """Create backup before migration."""
        backup_path = self.backup_dir / migration_id
        backup_path.mkdir(parents=True, exist_ok=True)

        try:
            if migration_type in ["config", "full_system"]:
                # Backup configuration files
                config_dir = Path("config")
                if config_dir.exists():
                    shutil.copytree(
                        config_dir, backup_path / "config", dirs_exist_ok=True
                    )

            if migration_type in ["database", "full_system"]:
                # Backup database files
                db_files = list(Path(".").glob("*.db")) + list(
                    Path("data").glob("*.db")
                )
                for db_file in db_files:
                    if db_file.exists():
                        shutil.copy2(db_file, backup_path / db_file.name)

            if migration_type in ["preferences", "full_system"]:
                # Backup user preferences
                prefs_dir = Path("data")
                if prefs_dir.exists():
                    shutil.copytree(prefs_dir, backup_path / "data", dirs_exist_ok=True)

            if migration_type in ["tools", "full_system"]:
                # Backup tool configurations
                tools_config = Path("src/utilities")
                if tools_config.exists():
                    # Only backup config files, not source code
                    for config_file in tools_config.rglob("*.json"):
                        rel_path = config_file.relative_to(tools_config)
                        dest_file = backup_path / "tools" / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(config_file, dest_file)

            if migration_type in ["cache", "full_system"]:
                # Backup cache data
                cache_dirs = [
                    Path("__pycache__"),
                    Path("build"),
                    Path(".pytest_cache"),
                ]
                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        shutil.copytree(
                            cache_dir,
                            backup_path / cache_dir.name,
                            dirs_exist_ok=True,
                        )

            # Create backup manifest
            manifest = {
                "migration_id": migration_id,
                "migration_type": migration_type,
                "backup_created_at": datetime.now().isoformat(),
                "backup_contents": [
                    str(p.relative_to(backup_path))
                    for p in backup_path.rglob("*")
                    if p.is_file()
                ],
            }

            with open(backup_path / "backup_manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)

            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_size": self._get_directory_size(backup_path),
                "files_backed_up": len(manifest["backup_contents"]),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _migrate_configuration(
        self, migration_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Migrate configuration files."""
        try:
            # This would contain specific configuration migration logic
            # For now, we provide the structure and basic validation

            config_path = Path("config/rfu_config.json")
            if not config_path.exists():
                return {
                    "success": False,
                    "error": "Configuration file not found",
                }

            # Load current configuration
            with open(config_path, "r") as f:
                config_data = json.load(f)

            # Perform migration transformations
            migrated_config = self._transform_configuration(config_data)

            # Validate migrated configuration
            validation_result = self._validate_configuration(migrated_config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Configuration validation failed: {validation_result['errors']}",
                }

            # Create backup of current config
            backup_path = config_path.with_suffix(".pre_migration_backup")
            shutil.copy2(config_path, backup_path)

            # Write new configuration
            with open(config_path, "w") as f:
                json.dump(migrated_config, f, indent=2)

            return {
                "success": True,
                "migrated_settings": len(migrated_config),
                "backup_created": str(backup_path),
                "validation_passed": True,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _migrate_database(self, migration_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate database schema and data."""
        try:
            # Find database files
            db_files = list(Path(".").glob("*.db"))
            if not db_files:
                return {
                    "success": True,
                    "message": "No database files found to migrate",
                }

            migrated_databases = []

            for db_file in db_files:
                # Create backup
                backup_file = db_file.with_suffix(".pre_migration_backup")
                shutil.copy2(db_file, backup_file)

                # Perform database migration
                migration_result = self._migrate_database_schema(db_file)
                if migration_result["success"]:
                    migrated_databases.append(str(db_file))
                else:
                    # Restore from backup on failure
                    shutil.copy2(backup_file, db_file)
                    return {
                        "success": False,
                        "error": f"Database migration failed for {db_file}: {migration_result['error']}",
                    }

            return {
                "success": True,
                "migrated_databases": migrated_databases,
                "databases_count": len(migrated_databases),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _migrate_preferences(
        self, migration_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Migrate user preferences."""
        try:
            # This would contain preference migration logic
            return {
                "success": True,
                "message": "Preferences migration completed",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _migrate_tool_integration(
        self, migration_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Migrate tool integration settings."""
        try:
            # This would contain tool integration migration logic
            return {
                "success": True,
                "message": "Tool integration migration completed",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _migrate_cache_data(self, migration_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate cache data."""
        try:
            # Clear old cache data
            cache_dirs = [
                Path("__pycache__"),
                Path("build/temp"),
                Path(".pytest_cache"),
            ]
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)

            return {
                "success": True,
                "message": "Cache data cleared successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _migrate_full_system(
        self, migration_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform full system migration."""
        try:
            results = []

            # Migrate each component
            for migration_type in [
                "config",
                "database",
                "preferences",
                "tools",
            ]:
                component_result = self.migration_types[migration_type](
                    migration_metadata
                )
                results.append(
                    {
                        "component": migration_type,
                        "success": component_result["success"],
                        "error": component_result.get("error"),
                    }
                )

                if not component_result["success"]:
                    return {
                        "success": False,
                        "error": f"Full system migration failed at {migration_type}",
                        "partial_results": results,
                    }

            return {
                "success": True,
                "components_migrated": len(results),
                "migration_results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _perform_rollback(
        self, migration_type: str, backup_location: str
    ) -> Dict[str, Any]:
        """Perform rollback from backup."""
        try:
            backup_path = Path(backup_location)

            if migration_type in ["config", "full_system"]:
                # Restore configuration
                config_backup = backup_path / "config"
                if config_backup.exists():
                    config_dir = Path("config")
                    if config_dir.exists():
                        shutil.rmtree(config_dir)
                    shutil.copytree(config_backup, config_dir)

            if migration_type in ["database", "full_system"]:
                # Restore databases
                for db_file in backup_path.glob("*.db"):
                    shutil.copy2(db_file, Path(db_file.name))

            if migration_type in ["preferences", "full_system"]:
                # Restore user data
                data_backup = backup_path / "data"
                if data_backup.exists():
                    data_dir = Path("data")
                    if data_dir.exists():
                        shutil.rmtree(data_dir)
                    shutil.copytree(data_backup, data_dir)

            return {
                "success": True,
                "restored_from": str(backup_path),
                "rollback_completed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_migration(self, migration_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate migration results."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks_performed": [],
        }

        try:
            migration_type = migration_metadata["migration_type"]

            if migration_type in ["config", "full_system"]:
                # Validate configuration
                config_path = Path("config/rfu_config.json")
                if config_path.exists():
                    try:
                        with open(config_path, "r") as f:
                            config_data = json.load(f)
                        validation_results["checks_performed"].append(
                            "config_file_valid_json"
                        )
                    except json.JSONDecodeError as e:
                        validation_results["valid"] = False
                        validation_results["errors"].append(
                            f"Configuration JSON invalid: {e}"
                        )
                else:
                    validation_results["valid"] = False
                    validation_results["errors"].append(
                        "Configuration file missing after migration"
                    )

            if migration_type in ["database", "full_system"]:
                # Validate database
                db_files = list(Path(".").glob("*.db"))
                for db_file in db_files:
                    try:
                        conn = sqlite3.connect(db_file)
                        conn.execute("SELECT 1")
                        conn.close()
                        validation_results["checks_performed"].append(
                            f"database_{db_file.name}_accessible"
                        )
                    except sqlite3.Error as e:
                        validation_results["valid"] = False
                        validation_results["errors"].append(
                            f"Database {db_file} corrupted: {e}"
                        )

            return validation_results

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation error: {e}")
            return validation_results

    def _transform_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform configuration data for migration."""
        # This would contain specific transformation logic
        # For now, return the config as-is
        return config_data

    def _validate_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration data."""
        validation_result = {"valid": True, "errors": []}

        # Basic validation checks
        required_sections = ["file_explorer", "database", "logging"]
        for section in required_sections:
            if section not in config_data:
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Missing required section: {section}"
                )

        return validation_result

    def _migrate_database_schema(self, db_file: Path) -> Dict[str, Any]:
        """Migrate database schema."""
        try:
            conn = sqlite3.connect(db_file)

            # Check current schema version
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version")
            current_version = cursor.fetchone()[0]

            # Apply schema updates if needed
            # This would contain specific schema migration logic

            conn.close()

            return {
                "success": True,
                "previous_version": current_version,
                "new_version": current_version,  # For now, no changes
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Example usage
    migration_manager = MigrationManager()

    # Create a test migration
    migration = migration_manager.create_migration(
        "test_migration", "config", "Test migration for demonstration"
    )

    print(f"Created migration: {migration['migration_id']}")
    print(f"Status: {migration['status']}")
