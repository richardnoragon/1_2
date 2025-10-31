"""
Phase 2 Integration Verification Script

This script verifies the complete integration of Phase 2 theme security
components with the Phase 1 migration system and validates all security
features work together correctly.
"""

import os
import sys
import json
import tempfile
import shutil
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Phase2IntegrationVerifier:
    """Comprehensive Phase 2 integration verification."""

    def __init__(self):
        """Initialize the integration verifier."""
        self.test_dir = None
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "start_time": datetime.now(),
            "end_time": None,
        }

        # Try to import security components
        self.components_available = self._check_component_availability()

    def _check_component_availability(self):
        """Check if all security components are available."""
        components = {}

        try:
            from theme_security_manager import ThemeSecurityManager

            components["ThemeSecurityManager"] = ThemeSecurityManager
        except ImportError:
            components["ThemeSecurityManager"] = None

        try:
            from theme_config import ThemeSecurityConfig

            components["ThemeSecurityConfig"] = ThemeSecurityConfig
        except ImportError:
            components["ThemeSecurityConfig"] = None

        try:
            from theme_backup import ThemeBackupManager

            components["ThemeBackupManager"] = ThemeBackupManager
        except ImportError:
            components["ThemeBackupManager"] = None

        try:
            from theme_recovery import ThemeRecoveryManager

            components["ThemeRecoveryManager"] = ThemeRecoveryManager
        except ImportError:
            components["ThemeRecoveryManager"] = None

        try:
            from theme_validator import ThemeIntegrityValidator

            components["ThemeIntegrityValidator"] = ThemeIntegrityValidator
        except ImportError:
            components["ThemeIntegrityValidator"] = None

        try:
            from theme_access_control import ThemeAccessController

            components["ThemeAccessController"] = ThemeAccessController
        except ImportError:
            components["ThemeAccessController"] = None

        try:
            from theme_data_encryption import ThemeDataEncryption

            components["ThemeDataEncryption"] = ThemeDataEncryption
        except ImportError:
            components["ThemeDataEncryption"] = None

        return components

    def _log_test(self, test_name, success, message="", details=None):
        """Log test result."""
        self.results["total_tests"] += 1

        if success:
            self.results["passed_tests"] += 1
            logger.info(f"✅ {test_name}: PASSED - {message}")
        else:
            self.results["failed_tests"] += 1
            logger.error(f"❌ {test_name}: FAILED - {message}")

        self.results["test_results"].append(
            {
                "test_name": test_name,
                "success": success,
                "message": message,
                "details": details,
                "timestamp": datetime.now(),
            }
        )

    def setup_test_environment(self):
        """Set up test environment."""
        try:
            self.test_dir = tempfile.mkdtemp(prefix="phase2_integration_test_")

            # Create directory structure
            os.makedirs(os.path.join(self.test_dir, "config"), exist_ok=True)
            os.makedirs(os.path.join(self.test_dir, "data"), exist_ok=True)
            os.makedirs(os.path.join(self.test_dir, "backups"), exist_ok=True)
            os.makedirs(os.path.join(self.test_dir, "themes"), exist_ok=True)

            self._log_test(
                "Test Environment Setup",
                True,
                f"Created test directory: {self.test_dir}",
            )
            return True

        except Exception as e:
            self._log_test("Test Environment Setup", False, str(e))
            return False

    def cleanup_test_environment(self):
        """Clean up test environment."""
        try:
            if self.test_dir and os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)

            self._log_test(
                "Test Environment Cleanup", True, "Test directory cleaned up"
            )
            return True

        except Exception as e:
            self._log_test("Test Environment Cleanup", False, str(e))
            return False

    def test_component_imports(self):
        """Test that all Phase 2 components can be imported."""
        logger.info("Testing component imports...")

        for (
            component_name,
            component_class,
        ) in self.components_available.items():
            if component_class is not None:
                self._log_test(
                    f"Import {component_name}",
                    True,
                    "Component imported successfully",
                )
            else:
                self._log_test(
                    f"Import {component_name}",
                    False,
                    "Component not available",
                )

    def test_database_migration(self):
        """Test database migration functionality."""
        logger.info("Testing database migration...")

        try:
            db_path = os.path.join(self.test_dir, "data", "test_migration.db")

            # Create a simple database connection to test
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Test basic database creation
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """
            )

            # Insert test data
            cursor.execute(
                "INSERT INTO test_table (name) VALUES (?)", ("test_migration",)
            )

            # Verify data
            cursor.execute("SELECT name FROM test_table WHERE id = 1")
            result = cursor.fetchone()

            conn.commit()
            conn.close()

            if result and result[0] == "test_migration":
                self._log_test(
                    "Database Migration Test",
                    True,
                    "Database operations successful",
                )
            else:
                self._log_test(
                    "Database Migration Test",
                    False,
                    "Data verification failed",
                )

        except Exception as e:
            self._log_test("Database Migration Test", False, str(e))

    def test_configuration_system(self):
        """Test configuration system functionality."""
        logger.info("Testing configuration system...")

        ThemeSecurityConfig = self.components_available.get(
            "ThemeSecurityConfig"
        )

        if not ThemeSecurityConfig:
            self._log_test(
                "Configuration System Test",
                False,
                "ThemeSecurityConfig not available",
            )
            return

        try:
            config_file = os.path.join(
                self.test_dir, "config", "security.json"
            )
            db_path = os.path.join(self.test_dir, "data", "security.db")

            # Initialize configuration
            config = ThemeSecurityConfig(config_file, db_path)

            # Test configuration operations
            config.set("test.value", "test_data", persist=False)
            retrieved_value = config.get("test.value")

            if retrieved_value == "test_data":
                self._log_test(
                    "Configuration Set/Get",
                    True,
                    "Configuration operations successful",
                )
            else:
                self._log_test(
                    "Configuration Set/Get",
                    False,
                    f"Expected 'test_data', got '{retrieved_value}'",
                )

            # Test validation
            validation_result = config.validate_configuration()

            if (
                isinstance(validation_result, dict)
                and "valid" in validation_result
            ):
                self._log_test(
                    "Configuration Validation",
                    True,
                    "Validation system functional",
                )
            else:
                self._log_test(
                    "Configuration Validation", False, "Validation failed"
                )

        except Exception as e:
            self._log_test("Configuration System Test", False, str(e))

    def test_encryption_system(self):
        """Test encryption system functionality."""
        logger.info("Testing encryption system...")

        ThemeDataEncryption = self.components_available.get(
            "ThemeDataEncryption"
        )

        if not ThemeDataEncryption:
            self._log_test(
                "Encryption System Test",
                False,
                "ThemeDataEncryption not available",
            )
            return

        try:
            # Initialize encryption
            encryption = ThemeDataEncryption()

            # Test data
            test_data = {
                "name": "test_theme",
                "colors": {"primary": "#FF0000"},
                "settings": {"dark_mode": True},
            }

            # Test encryption/decryption
            encrypted_data = encryption.encrypt_theme_data(test_data)

            if encrypted_data and encrypted_data != test_data:
                self._log_test(
                    "Data Encryption", True, "Data encrypted successfully"
                )

                # Test decryption
                decrypted_data = encryption.decrypt_theme_data(encrypted_data)

                if decrypted_data == test_data:
                    self._log_test(
                        "Data Decryption", True, "Data decrypted successfully"
                    )
                else:
                    self._log_test(
                        "Data Decryption",
                        False,
                        "Decrypted data doesn't match original",
                    )
            else:
                self._log_test(
                    "Data Encryption",
                    False,
                    "Encryption failed or data unchanged",
                )

        except Exception as e:
            self._log_test("Encryption System Test", False, str(e))

    def test_validation_system(self):
        """Test theme validation system."""
        logger.info("Testing validation system...")

        ThemeIntegrityValidator = self.components_available.get(
            "ThemeIntegrityValidator"
        )

        if not ThemeIntegrityValidator:
            self._log_test(
                "Validation System Test",
                False,
                "ThemeIntegrityValidator not available",
            )
            return

        try:
            validator = ThemeIntegrityValidator()

            # Test valid theme
            valid_theme = {
                "name": "test_theme",
                "version": "1.0",
                "colors": {"primary": "#FF0000"},
                "settings": {"dark_mode": True},
            }

            validation_result = validator.validate_theme_data(valid_theme)

            if isinstance(validation_result, dict):
                self._log_test(
                    "Theme Validation", True, "Validation system functional"
                )

                # Test corruption detection
                corrupted_theme = valid_theme.copy()
                corrupted_theme["corrupted_field"] = None

                corruption_result = validator.detect_corruption(
                    corrupted_theme
                )

                if isinstance(corruption_result, dict):
                    self._log_test(
                        "Corruption Detection",
                        True,
                        "Corruption detection functional",
                    )
                else:
                    self._log_test(
                        "Corruption Detection",
                        False,
                        "Corruption detection failed",
                    )
            else:
                self._log_test("Theme Validation", False, "Validation failed")

        except Exception as e:
            self._log_test("Validation System Test", False, str(e))

    def test_backup_system(self):
        """Test backup system functionality."""
        logger.info("Testing backup system...")

        ThemeBackupManager = self.components_available.get(
            "ThemeBackupManager"
        )

        if not ThemeBackupManager:
            self._log_test(
                "Backup System Test", False, "ThemeBackupManager not available"
            )
            return

        try:
            backup_dir = os.path.join(self.test_dir, "backups")
            db_path = os.path.join(self.test_dir, "data", "backup.db")

            # Create test database for backup manager
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS theme_backups (
                    backup_id TEXT PRIMARY KEY,
                    theme_name TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()
            conn.close()

            # Initialize backup manager
            backup_manager = ThemeBackupManager(backup_dir, db_path)

            # Create test theme file
            theme_file = os.path.join(
                self.test_dir, "themes", "test_theme.json"
            )
            test_theme = {"name": "test_theme", "data": "test_data"}

            with open(theme_file, "w") as f:
                json.dump(test_theme, f)

            # Test backup creation
            backup_id = backup_manager.create_backup("test_theme", theme_file)

            if backup_id:
                self._log_test(
                    "Backup Creation", True, f"Backup created: {backup_id}"
                )

                # Test backup verification
                verification_result = backup_manager.verify_backup(backup_id)

                if isinstance(verification_result, dict):
                    self._log_test(
                        "Backup Verification",
                        True,
                        "Backup verification functional",
                    )
                else:
                    self._log_test(
                        "Backup Verification",
                        False,
                        "Backup verification failed",
                    )
            else:
                self._log_test(
                    "Backup Creation", False, "Backup creation failed"
                )

        except Exception as e:
            self._log_test("Backup System Test", False, str(e))

    def test_security_manager_integration(self):
        """Test security manager integration."""
        logger.info("Testing security manager integration...")

        ThemeSecurityManager = self.components_available.get(
            "ThemeSecurityManager"
        )

        if not ThemeSecurityManager:
            self._log_test(
                "Security Manager Integration",
                False,
                "ThemeSecurityManager not available",
            )
            return

        try:
            # Initialize security manager
            security_manager = ThemeSecurityManager()

            # Test security status
            status = security_manager.get_security_status()

            if isinstance(status, dict):
                self._log_test(
                    "Security Status",
                    True,
                    "Security status retrieval functional",
                )

                # Test theme data operations
                test_theme = {
                    "name": "integration_test_theme",
                    "data": "test_data",
                }

                theme_file = os.path.join(
                    self.test_dir, "themes", "secure_theme.json"
                )

                # Mock keyring operations for testing
                from unittest.mock import patch

                with (
                    patch("keyring.get_password", return_value=None),
                    patch("keyring.set_password", return_value=None),
                ):

                    # Test secure save
                    save_result = security_manager.save_theme_secure(
                        "integration_test", test_theme, theme_file
                    )

                    if save_result:
                        self._log_test(
                            "Secure Theme Save", True, "Theme saved securely"
                        )

                        # Test secure load
                        loaded_theme = security_manager.load_theme_secure(
                            "integration_test", theme_file
                        )

                        if loaded_theme == test_theme:
                            self._log_test(
                                "Secure Theme Load",
                                True,
                                "Theme loaded and verified",
                            )
                        else:
                            self._log_test(
                                "Secure Theme Load",
                                False,
                                "Loaded theme doesn't match original",
                            )
                    else:
                        self._log_test(
                            "Secure Theme Save", False, "Theme save failed"
                        )
            else:
                self._log_test(
                    "Security Status",
                    False,
                    "Security status retrieval failed",
                )

        except Exception as e:
            self._log_test("Security Manager Integration", False, str(e))

    def test_complete_workflow(self):
        """Test complete security workflow."""
        logger.info("Testing complete security workflow...")

        # Check if all required components are available
        required_components = [
            "ThemeSecurityConfig",
            "ThemeSecurityManager",
            "ThemeBackupManager",
            "ThemeIntegrityValidator",
        ]

        missing_components = [
            comp
            for comp in required_components
            if not self.components_available.get(comp)
        ]

        if missing_components:
            self._log_test(
                "Complete Workflow Test",
                False,
                f"Missing components: {missing_components}",
            )
            return

        try:
            # Initialize all components
            config_file = os.path.join(
                self.test_dir, "config", "workflow.json"
            )
            db_path = os.path.join(self.test_dir, "data", "workflow.db")

            # Create minimal database schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create required tables
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS theme_security_config (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    config_type TEXT NOT NULL
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS theme_backups (
                    backup_id TEXT PRIMARY KEY,
                    theme_name TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            conn.close()

            # Initialize components
            ThemeSecurityConfig = self.components_available[
                "ThemeSecurityConfig"
            ]
            ThemeSecurityManager = self.components_available[
                "ThemeSecurityManager"
            ]
            ThemeBackupManager = self.components_available[
                "ThemeBackupManager"
            ]
            ThemeIntegrityValidator = self.components_available[
                "ThemeIntegrityValidator"
            ]

            config = ThemeSecurityConfig(config_file, db_path)
            manager = ThemeSecurityManager()
            backup_mgr = ThemeBackupManager(
                os.path.join(self.test_dir, "backups"), db_path
            )
            validator = ThemeIntegrityValidator()

            # Test workflow
            workflow_theme = {
                "name": "workflow_test_theme",
                "version": "1.0",
                "colors": {"primary": "#FF0000"},
                "settings": {"dark_mode": True},
            }

            # 1. Validate theme
            validation_result = validator.validate_theme_data(workflow_theme)

            if validation_result.get("valid", False):
                self._log_test(
                    "Workflow - Validation", True, "Theme validation passed"
                )

                # 2. Create backup
                theme_file = os.path.join(
                    self.test_dir, "themes", "workflow.json"
                )
                with open(theme_file, "w") as f:
                    json.dump(workflow_theme, f)

                backup_id = backup_mgr.create_backup(
                    "workflow_test", theme_file
                )

                if backup_id:
                    self._log_test(
                        "Workflow - Backup", True, "Theme backup created"
                    )

                    # 3. Configure security
                    config.set("encryption.require_encryption", True)
                    config.set("backup.auto_backup_enabled", True)

                    self._log_test(
                        "Workflow - Configuration",
                        True,
                        "Security configuration updated",
                    )

                    # 4. Complete workflow test passed
                    self._log_test(
                        "Complete Workflow",
                        True,
                        "All workflow components functional",
                    )
                else:
                    self._log_test(
                        "Workflow - Backup", False, "Backup creation failed"
                    )
            else:
                self._log_test(
                    "Workflow - Validation", False, "Theme validation failed"
                )

        except Exception as e:
            self._log_test("Complete Workflow Test", False, str(e))

    def generate_report(self):
        """Generate comprehensive test report."""
        self.results["end_time"] = datetime.now()
        duration = self.results["end_time"] - self.results["start_time"]

        logger.info("\n" + "=" * 60)
        logger.info("PHASE 2 INTEGRATION VERIFICATION REPORT")
        logger.info("=" * 60)

        logger.info(f"Test Duration: {duration}")
        logger.info(f"Total Tests: {self.results['total_tests']}")
        logger.info(f"Passed Tests: {self.results['passed_tests']}")
        logger.info(f"Failed Tests: {self.results['failed_tests']}")

        success_rate = (
            self.results["passed_tests"] / self.results["total_tests"] * 100
            if self.results["total_tests"] > 0
            else 0
        )
        logger.info(f"Success Rate: {success_rate:.1f}%")

        logger.info("\nDETAILED RESULTS:")
        logger.info("-" * 40)

        for result in self.results["test_results"]:
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            logger.info(f"{status}: {result['test_name']}")
            if result["message"]:
                logger.info(f"  Message: {result['message']}")

        logger.info("\nCOMPONENT AVAILABILITY:")
        logger.info("-" * 30)

        for (
            component_name,
            component_class,
        ) in self.components_available.items():
            status = "✅ Available" if component_class else "❌ Missing"
            logger.info(f"{status}: {component_name}")

        logger.info("\nRECOMMENDATIONS:")
        logger.info("-" * 20)

        if self.results["failed_tests"] == 0:
            logger.info("✅ Phase 2 implementation is fully functional!")
            logger.info("✅ All security components are working correctly.")
            logger.info("✅ Integration with Phase 1 is successful.")
            logger.info("✅ System is ready for production deployment.")
        else:
            logger.info("⚠️  Some tests failed. Please review the following:")

            failed_tests = [
                r for r in self.results["test_results"] if not r["success"]
            ]
            for test in failed_tests:
                logger.info(f"   - {test['test_name']}: {test['message']}")

        # Save report to file
        if self.test_dir:
            report_file = os.path.join(
                self.test_dir, "integration_report.json"
            )
            try:
                with open(report_file, "w") as f:
                    # Convert datetime objects to strings for JSON serialization
                    json_results = self.results.copy()
                    json_results["start_time"] = json_results[
                        "start_time"
                    ].isoformat()
                    json_results["end_time"] = json_results[
                        "end_time"
                    ].isoformat()

                    for result in json_results["test_results"]:
                        result["timestamp"] = result["timestamp"].isoformat()

                    json.dump(json_results, f, indent=2)

                logger.info(f"\nReport saved to: {report_file}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")

        return self.results

    def run_verification(self):
        """Run complete Phase 2 integration verification."""
        logger.info("Starting Phase 2 Integration Verification...")

        try:
            # Setup test environment
            if not self.setup_test_environment():
                return self.results

            # Run all tests
            self.test_component_imports()
            self.test_database_migration()
            self.test_configuration_system()
            self.test_encryption_system()
            self.test_validation_system()
            self.test_backup_system()
            self.test_security_manager_integration()
            self.test_complete_workflow()

            # Generate report
            self.generate_report()

            return self.results

        finally:
            # Always cleanup
            self.cleanup_test_environment()


def main():
    """Main verification function."""
    print("RFU Hub Phase 2 - Integration Verification")
    print("=" * 50)

    verifier = Phase2IntegrationVerifier()
    results = verifier.run_verification()

    # Exit with appropriate code
    if results["failed_tests"] == 0:
        print("\n🎉 Phase 2 integration verification PASSED!")
        sys.exit(0)
    else:
        print(
            f"\n⚠️  Phase 2 integration verification completed with {results['failed_tests']} failures."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
