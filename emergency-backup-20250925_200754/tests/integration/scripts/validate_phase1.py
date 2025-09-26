#!/usr/bin/env python3
"""
Phase 1 Setup Validation Script
RFU Integration Testing - Foundation Setup Validation

This script validates the complete Phase 1 implementation and generates
a comprehensive readiness report for Phase 2 transition.
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


class Phase1Validator:
    """Comprehensive validation for Phase 1 foundation setup."""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.project_root = self.base_path.parent
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 1 - Foundation Setup",
            "overall_status": "unknown",
            "completion_percentage": 0,
            "components": {},
            "recommendations": [],
            "phase2_readiness": False,
        }

    def validate_all(self) -> Dict[str, Any]:
        """Run complete Phase 1 validation."""
        print("🧪 RFU Integration Testing - Phase 1 Validation")
        print("=" * 60)

        # Component validations
        components = [
            ("Environment Configurations", self.validate_environment_configs),
            ("Directory Structure", self.validate_directory_structure),
            ("CI/CD Pipeline", self.validate_cicd_pipeline),
            ("Monitoring System", self.validate_monitoring_system),
            ("Test Framework", self.validate_test_framework),
            ("Dependencies", self.validate_dependencies),
            ("Environment Management", self.validate_environment_manager),
            ("Test Data", self.validate_test_data),
            ("Documentation", self.validate_documentation),
        ]

        total_score = 0
        max_score = len(components) * 100

        for component_name, validator_func in components:
            print(f"\n📋 Validating {component_name}...")

            try:
                result = validator_func()
                self.validation_results["components"][component_name] = result
                total_score += result["score"]

                status_emoji = (
                    "✅"
                    if result["status"] == "pass"
                    else "❌" if result["status"] == "fail" else "⚠️"
                )
                print(
                    f"{status_emoji} {component_name}: {result['status'].upper()} ({result['score']}/100)"
                )

                if result.get("issues"):
                    for issue in result["issues"]:
                        print(f"   ⚠️ {issue}")

            except Exception as e:
                print(f"❌ {component_name}: ERROR - {str(e)}")
                self.validation_results["components"][component_name] = {
                    "status": "error",
                    "score": 0,
                    "issues": [str(e)],
                }

        # Calculate overall metrics
        self.validation_results["completion_percentage"] = round(
            (total_score / max_score) * 100, 1
        )

        # Determine overall status
        if self.validation_results["completion_percentage"] >= 90:
            self.validation_results["overall_status"] = "excellent"
        elif self.validation_results["completion_percentage"] >= 75:
            self.validation_results["overall_status"] = "good"
        elif self.validation_results["completion_percentage"] >= 50:
            self.validation_results["overall_status"] = "fair"
        else:
            self.validation_results["overall_status"] = "poor"

        # Assess Phase 2 readiness
        critical_components = [
            "Environment Configurations",
            "Test Framework",
            "Dependencies",
        ]
        phase2_ready = all(
            self.validation_results["components"].get(comp, {}).get("score", 0)
            >= 80
            for comp in critical_components
        )
        self.validation_results["phase2_readiness"] = phase2_ready

        # Generate recommendations
        self._generate_recommendations()

        # Display summary
        self._display_summary()

        # Save results
        self._save_results()

        return self.validation_results

    def validate_environment_configs(self) -> Dict[str, Any]:
        """Validate environment configuration files."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        environments = ["dev", "staging", "prod-like"]

        for env in environments:
            config_path = self.base_path / "environments" / env / "config.yaml"

            if not config_path.exists():
                result["issues"].append(
                    f"Missing config for {env} environment"
                )
                result["score"] -= 30
                continue

            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)

                # Validate required sections
                required_sections = [
                    "environment",
                    "database",
                    "network",
                    "logging",
                    "performance",
                ]
                missing_sections = [
                    section
                    for section in required_sections
                    if section not in config
                ]

                if missing_sections:
                    result["issues"].append(
                        f"{env}: Missing sections: {missing_sections}"
                    )
                    result["score"] -= 10

                result["details"][env] = {
                    "config_valid": True,
                    "sections": list(config.keys()),
                    "missing_sections": missing_sections,
                }

            except yaml.YAMLError as e:
                result["issues"].append(f"{env}: Invalid YAML - {str(e)}")
                result["score"] -= 20
                result["details"][env] = {
                    "config_valid": False,
                    "error": str(e),
                }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_directory_structure(self) -> Dict[str, Any]:
        """Validate required directory structure."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        required_dirs = [
            "environments",
            "environments/dev",
            "environments/staging",
            "environments/prod-like",
            "scripts",
            "configs",
            "monitoring",
            "data",
            "artifacts",
            "backups",
            "logs",
        ]

        missing_dirs = []
        existing_dirs = []

        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)
                result["score"] -= 10

        if missing_dirs:
            result["issues"].append(f"Missing directories: {missing_dirs}")

        result["details"] = {
            "existing_dirs": existing_dirs,
            "missing_dirs": missing_dirs,
            "total_required": len(required_dirs),
            "total_existing": len(existing_dirs),
        }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_cicd_pipeline(self) -> Dict[str, Any]:
        """Validate CI/CD pipeline configuration."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        workflow_path = (
            self.base_path.parent.parent
            / ".github"
            / "workflows"
            / "integration-tests.yml"
        )

        if not workflow_path.exists():
            result["issues"].append("GitHub Actions workflow file not found")
            result["score"] = 0
            result["status"] = "fail"
            return result

        try:
            with open(
                workflow_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                workflow_content = f.read()

            # Check for required workflow components
            required_components = [
                "RFU Integration Tests",
                "setup-environment",
                "smoke-tests",
                "integration-tests",
                "performance-tests",
                "security-tests",
            ]

            missing_components = []
            for component in required_components:
                if component not in workflow_content:
                    missing_components.append(component)
                    result["score"] -= 15

            if missing_components:
                result["issues"].append(
                    f"Missing workflow components: {missing_components}"
                )

            # Check for environment matrix
            if "matrix:" not in workflow_content:
                result["issues"].append(
                    "Missing matrix strategy for multi-environment testing"
                )
                result["score"] -= 10

            result["details"] = {
                "workflow_exists": True,
                "missing_components": missing_components,
                "has_matrix_strategy": "matrix:" in workflow_content,
                "file_size": len(workflow_content),
            }

        except Exception as e:
            result["issues"].append(f"Error reading workflow file: {str(e)}")
            result["score"] -= 50

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_monitoring_system(self) -> Dict[str, Any]:
        """Validate monitoring and alerting system."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        # Check monitoring script
        monitor_script = self.base_path / "monitoring" / "system_monitor.py"
        if not monitor_script.exists():
            result["issues"].append("System monitor script not found")
            result["score"] -= 40

        # Check monitoring config
        monitor_config = self.base_path / "configs" / "monitoring_config.yaml"
        if not monitor_config.exists():
            result["issues"].append("Monitoring configuration not found")
            result["score"] -= 30
        else:
            try:
                with open(monitor_config, "r") as f:
                    config = yaml.safe_load(f)

                required_sections = ["monitoring", "thresholds", "alerting"]
                missing_sections = [
                    section
                    for section in required_sections
                    if section not in config
                ]

                if missing_sections:
                    result["issues"].append(
                        f"Missing monitoring config sections: {missing_sections}"
                    )
                    result["score"] -= 20

            except yaml.YAMLError as e:
                result["issues"].append(f"Invalid monitoring config: {str(e)}")
                result["score"] -= 30

        result["details"] = {
            "monitor_script_exists": monitor_script.exists(),
            "config_exists": monitor_config.exists(),
            "monitoring_dir_exists": (self.base_path / "monitoring").exists(),
        }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_test_framework(self) -> Dict[str, Any]:
        """Validate test framework components."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        # Check key scripts
        required_scripts = [
            "scripts/environment_manager.py",
            "scripts/generate_test_report.py",
            "scripts/setup_environment.py",
        ]

        missing_scripts = []
        for script_path in required_scripts:
            full_path = self.base_path / script_path
            if not full_path.exists():
                missing_scripts.append(script_path)
                result["score"] -= 25

        if missing_scripts:
            result["issues"].append(f"Missing scripts: {missing_scripts}")

        # Check test requirements
        test_req_path = self.base_path / "requirements-test.txt"
        if not test_req_path.exists():
            result["issues"].append("Test requirements file not found")
            result["score"] -= 20
        else:
            with open(test_req_path, "r") as f:
                requirements = f.read()

            essential_packages = ["pytest", "pytest-cov", "PyYAML", "psutil"]
            missing_packages = []

            for package in essential_packages:
                if package not in requirements:
                    missing_packages.append(package)
                    result["score"] -= 5

            if missing_packages:
                result["issues"].append(
                    f"Missing essential packages: {missing_packages}"
                )

        result["details"] = {
            "missing_scripts": missing_scripts,
            "test_requirements_exists": test_req_path.exists(),
            "scripts_count": len(required_scripts) - len(missing_scripts),
        }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate Python dependencies and environment."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        # Check Python version
        version = sys.version_info
        if version.major != 3 or version.minor < 8:
            result["issues"].append(
                f"Python {version.major}.{version.minor} detected. Python 3.8+ required."
            )
            result["score"] -= 50

        # Check virtual environment
        venv_path = self.project_root / "venv"
        venv_exists = venv_path.exists()

        if not venv_exists:
            result["issues"].append("Virtual environment not found")
            result["score"] -= 20

        # Check if we can import key modules
        test_imports = [
            ("pytest", "Testing framework"),
            ("yaml", "YAML processing"),
            ("psutil", "System monitoring"),
            ("sqlite3", "Database testing"),
        ]

        failed_imports = []
        for module_name, description in test_imports:
            try:
                __import__(module_name)
            except ImportError:
                failed_imports.append(f"{module_name} ({description})")
                result["score"] -= 10

        if failed_imports:
            result["issues"].append(f"Failed to import: {failed_imports}")

        result["details"] = {
            "python_version": f"{version.major}.{version.minor}.{version.micro}",
            "python_compatible": version.major == 3 and version.minor >= 8,
            "venv_exists": venv_exists,
            "failed_imports": failed_imports,
        }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_environment_manager(self) -> Dict[str, Any]:
        """Validate environment manager functionality."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        env_manager_path = (
            self.base_path / "scripts" / "environment_manager.py"
        )

        if not env_manager_path.exists():
            result["issues"].append("Environment manager script not found")
            result["score"] = 0
            result["status"] = "fail"
            return result

        try:
            # Add scripts directory to Python path
            sys.path.insert(0, str(self.base_path / "scripts"))

            from environment_manager import EnvironmentManager

            manager = EnvironmentManager(str(self.base_path))

            # Test basic functionality
            environments = manager.list_environments()

            if not environments:
                result["issues"].append("No environments configured")
                result["score"] -= 30

            # Check if environments can be validated
            for env in environments:
                if env.get("created", False):
                    try:
                        validation = manager.validate_environment(env["name"])
                        if validation["overall_status"] != "healthy":
                            result["issues"].append(
                                f"Environment {env['name']} validation failed"
                            )
                            result["score"] -= 15
                    except Exception as e:
                        result["issues"].append(
                            f"Error validating {env['name']}: {str(e)}"
                        )
                        result["score"] -= 10

            result["details"] = {
                "manager_functional": True,
                "environments_count": len(environments),
                "environments_created": len(
                    [e for e in environments if e.get("created", False)]
                ),
            }

        except ImportError as e:
            result["issues"].append(
                f"Cannot import environment manager: {str(e)}"
            )
            result["score"] -= 60
        except Exception as e:
            result["issues"].append(f"Environment manager error: {str(e)}")
            result["score"] -= 40

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_test_data(self) -> Dict[str, Any]:
        """Validate test data and database setup."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        environments = ["dev", "staging", "prod-like"]
        db_status = {}

        for env in environments:
            db_path = self.base_path / f"data/test_{env}.db"

            if not db_path.exists():
                result["issues"].append(
                    f"Database not found for {env} environment"
                )
                result["score"] -= 20
                db_status[env] = "missing"
                continue

            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()

                # Check for basic tables
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in cursor.fetchall()]

                expected_tables = [
                    "files",
                    "file_metadata",
                    "processing_jobs",
                    "user_preferences",
                ]
                missing_tables = [
                    table for table in expected_tables if table not in tables
                ]

                if missing_tables:
                    result["issues"].append(
                        f"{env} database missing tables: {missing_tables}"
                    )
                    result["score"] -= 10

                # Check if tables have data
                cursor.execute("SELECT COUNT(*) FROM files")
                file_count = cursor.fetchone()[0]

                conn.close()

                db_status[env] = {
                    "exists": True,
                    "tables": tables,
                    "missing_tables": missing_tables,
                    "file_count": file_count,
                }

            except sqlite3.Error as e:
                result["issues"].append(f"Database error for {env}: {str(e)}")
                result["score"] -= 15
                db_status[env] = "error"

        result["details"] = {
            "databases": db_status,
            "total_environments": len(environments),
        }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness."""
        result = {"status": "pass", "score": 100, "issues": [], "details": {}}

        # Check main integration test overview
        overview_path = self.base_path / "integration_test_overview.md"
        if not overview_path.exists():
            result["issues"].append("Integration test overview not found")
            result["score"] -= 40
        else:
            with open(
                overview_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                content = f.read()

            # Check for Phase 1 completion status
            if "Phase 1: Foundation Setup" not in content:
                result["issues"].append(
                    "Phase 1 section not found in overview"
                )
                result["score"] -= 20

            if "✅ COMPLETED" not in content:
                result["issues"].append(
                    "Phase 1 completion status not updated"
                )
                result["score"] -= 20

        # Check for README files
        readme_locations = [
            self.base_path / "README.md",
            self.project_root / "README.md",
        ]

        readme_exists = any(path.exists() for path in readme_locations)
        if not readme_exists:
            result["issues"].append("No README file found")
            result["score"] -= 20

        result["details"] = {
            "overview_exists": overview_path.exists(),
            "readme_exists": readme_exists,
            "documentation_updated": True,
        }

        if result["score"] < 50:
            result["status"] = "fail"
        elif result["score"] < 80:
            result["status"] = "warning"

        return result

    def _generate_recommendations(self):
        """Generate recommendations based on validation results."""
        recommendations = []

        # Check for critical failures
        for component, result in self.validation_results["components"].items():
            if result["status"] == "fail":
                recommendations.append(
                    f"🔴 CRITICAL: Fix {component} issues before proceeding to Phase 2"
                )
            elif result["status"] == "warning":
                recommendations.append(
                    f"🟡 WARNING: Address {component} issues for optimal Phase 2 performance"
                )

        # Overall recommendations
        completion = self.validation_results["completion_percentage"]

        if completion >= 90:
            recommendations.append(
                "🎉 Excellent! Phase 1 setup is complete and ready for Phase 2"
            )
        elif completion >= 75:
            recommendations.append(
                "✅ Good setup. Minor improvements recommended before Phase 2"
            )
        elif completion >= 50:
            recommendations.append(
                "⚠️ Fair setup. Address warning issues before proceeding"
            )
        else:
            recommendations.append(
                "❌ Poor setup. Significant work needed before Phase 2"
            )

        # Phase 2 readiness
        if self.validation_results["phase2_readiness"]:
            recommendations.append(
                "🚀 Ready to proceed with Phase 2: Core Integration Tests"
            )
        else:
            recommendations.append(
                "⛔ Not ready for Phase 2. Address critical component issues first"
            )

        self.validation_results["recommendations"] = recommendations

    def _display_summary(self):
        """Display validation summary."""
        print("\n" + "=" * 60)
        print("📊 PHASE 1 VALIDATION SUMMARY")
        print("=" * 60)

        status_emoji = {
            "excellent": "🎉",
            "good": "✅",
            "fair": "⚠️",
            "poor": "❌",
        }

        overall_status = self.validation_results["overall_status"]
        completion = self.validation_results["completion_percentage"]

        print(
            f"{status_emoji.get(overall_status, '❓')} Overall Status: {overall_status.upper()}"
        )
        print(f"📈 Completion: {completion}%")
        print(
            f"🎯 Phase 2 Ready: {'YES' if self.validation_results['phase2_readiness'] else 'NO'}"
        )

        print(f"\n📋 Component Status:")
        for component, result in self.validation_results["components"].items():
            status_emoji_map = {
                "pass": "✅",
                "warning": "⚠️",
                "fail": "❌",
                "error": "💥",
            }
            emoji = status_emoji_map.get(result["status"], "❓")
            print(f"   {emoji} {component}: {result['score']}/100")

        print(f"\n💡 Recommendations:")
        for rec in self.validation_results["recommendations"]:
            print(f"   {rec}")

        print("\n" + "=" * 60)

    def _save_results(self):
        """Save validation results to file."""
        results_file = (
            self.base_path
            / "artifacts"
            / f"phase1_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        print(f"📄 Validation results saved to: {results_file}")


def main():
    """Main function for command-line usage."""
    print("Starting Phase 1 Foundation Setup Validation...")

    validator = Phase1Validator()
    results = validator.validate_all()

    # Exit with appropriate code
    if results["phase2_readiness"]:
        print("\n🎉 Phase 1 validation completed successfully!")
        print("🚀 Ready to proceed with Phase 2: Core Integration Tests")
        sys.exit(0)
    else:
        print("\n⚠️ Phase 1 validation completed with issues.")
        print(
            "🔧 Please address the issues above before proceeding to Phase 2."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
