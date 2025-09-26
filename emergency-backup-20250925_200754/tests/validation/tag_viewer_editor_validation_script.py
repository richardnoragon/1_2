#!/usr/bin/env python3
"""
Tag Viewer Editor Migration Validation Script

This script performs comprehensive post-migration validation for the tag_viewer_editor files
that have been migrated to file_utilities_2/gui/. It validates:

1. Migration integrity through checksum comparison
2. PyQt5 compatibility testing
3. Import functionality validation
4. Integration testing with RFU Hub
5. Backup system verification

Author: Debug Mode Validation System
Date: 2025-07-27
"""

import os
import sys
import hashlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import traceback


class TagViewerEditorValidator:
    """Comprehensive validation system for tag_viewer_editor migration."""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.validation_results = {
            "file_structure": {},
            "checksums": {},
            "pyqt5_compatibility": {},
            "import_validation": {},
            "integration_tests": {},
            "backup_verification": {},
            "issues_found": [],
            "recommendations": [],
        }

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for a file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information."""
        try:
            stat = file_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "checksum": self.calculate_file_checksum(file_path),
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "modified_time": stat.st_mtime,
            }
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def validate_file_structure(self) -> Dict[str, Any]:
        """Validate the current file structure and locations."""
        print("🔍 Validating file structure...")

        files_to_check = {
            "migrated_py": Path("file_utilities_2/gui/tag_viewer_editor.py"),
            "migrated_ui": Path("file_utilities_2/gui/tag_viewer_editor.ui"),
            "legacy_py": Path("tag_viewer_editor.py"),
            "legacy_ui": Path("tag_viewer_editor.ui"),
            "backup_py": Path(
                "backup/tag_viewer_editor_migration/2025-01-27_14-16-46/tag_viewer_editor.py"
            ),
            "backup_ui": Path(
                "backup/tag_viewer_editor_migration/2025-01-27_14-16-46/tag_viewer_editor.ui"
            ),
            "backup_manifest": Path(
                "backup/tag_viewer_editor_migration/2025-01-27_14-16-46/backup_manifest.txt"
            ),
            "rfuhub": Path("rfuhub.py"),
        }

        results = {}
        for file_key, file_path in files_to_check.items():
            results[file_key] = self.get_file_info(file_path)

        return results

    def validate_migration_integrity(self) -> Dict[str, Any]:
        """Validate migration integrity through checksum comparison."""
        print("🔐 Validating migration integrity...")

        # Compare migrated files with backup files
        comparisons = [
            ("migrated_py", "backup_py", "Python file integrity"),
            ("migrated_ui", "backup_ui", "UI file integrity"),
            ("legacy_py", "backup_py", "Legacy vs backup Python"),
            ("legacy_ui", "backup_ui", "Legacy vs backup UI"),
        ]

        results = {}
        file_info = self.validation_results["file_structure"]

        for file1_key, file2_key, description in comparisons:
            file1_info = file_info.get(file1_key, {})
            file2_info = file_info.get(file2_key, {})

            if file1_info.get("exists") and file2_info.get("exists"):
                checksum1 = file1_info.get("checksum")
                checksum2 = file2_info.get("checksum")

                results[description] = {
                    "file1_checksum": checksum1,
                    "file2_checksum": checksum2,
                    "match": checksum1 == checksum2,
                    "file1_size": file1_info.get("size"),
                    "file2_size": file2_info.get("size"),
                    "size_match": file1_info.get("size")
                    == file2_info.get("size"),
                }
            else:
                results[description] = {
                    "error": f"One or both files missing: {file1_key}={file1_info.get('exists')}, {file2_key}={file2_info.get('exists')}"
                }

        return results

    def test_pyqt5_compatibility(self) -> Dict[str, Any]:
        """Test PyQt5 compatibility in migrated files."""
        print("🧪 Testing PyQt5 compatibility...")

        results = {
            "pyqt5_available": False,
            "import_tests": {},
            "ui_loading_test": {},
            "class_instantiation": {},
        }

        # Test PyQt5 availability
        try:
            import PyQt5.QtWidgets
            import PyQt5.QtCore
            import PyQt5.QtGui
            from PyQt5 import uic

            results["pyqt5_available"] = True
            results["pyqt5_version"] = getattr(
                PyQt5.QtCore, "PYQT_VERSION_STR", "Unknown"
            )
        except ImportError as e:
            results["pyqt5_available"] = False
            results["pyqt5_error"] = str(e)
            return results

        # Test imports from migrated file
        try:
            # Add file_utilities_2 to path temporarily
            sys.path.insert(0, str(self.base_dir))

            # Test direct import
            from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor

            results["import_tests"]["direct_import"] = {
                "success": True,
                "class_found": True,
                "class_type": str(type(TagViewerEditor)),
            }

            # Test class inspection
            import inspect

            results["import_tests"]["class_methods"] = [
                method
                for method in dir(TagViewerEditor)
                if not method.startswith("_") or method in ["__init__"]
            ]

            # Test UI file loading
            ui_file = (
                self.base_dir / "file_utilities_2/gui/tag_viewer_editor.ui"
            )
            if ui_file.exists():
                try:
                    # Create a temporary widget to test UI loading
                    from PyQt5.QtWidgets import QMainWindow

                    temp_widget = QMainWindow()
                    uic.loadUi(str(ui_file), temp_widget)
                    results["ui_loading_test"] = {
                        "success": True,
                        "ui_file_path": str(ui_file),
                        "widgets_found": [
                            attr
                            for attr in dir(temp_widget)
                            if not attr.startswith("_")
                            and hasattr(
                                getattr(temp_widget, attr), "objectName"
                            )
                        ],
                    }
                except Exception as e:
                    results["ui_loading_test"] = {
                        "success": False,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }

        except Exception as e:
            results["import_tests"]["direct_import"] = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        finally:
            # Remove from path
            if str(self.base_dir) in sys.path:
                sys.path.remove(str(self.base_dir))

        return results

    def validate_import_statements(self) -> Dict[str, Any]:
        """Search for and validate import statement references."""
        print("📋 Validating import statements...")

        results = {
            "rfuhub_integration": {},
            "old_import_references": [],
            "new_import_validation": {},
        }

        # Check RFU Hub integration
        rfuhub_file = self.base_dir / "rfuhub.py"
        if rfuhub_file.exists():
            try:
                with open(rfuhub_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for new import pattern
                new_import_found = (
                    "from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor"
                    in content
                )
                old_import_found = (
                    "from tag_viewer_editor import TagViewerEditor" in content
                )

                results["rfuhub_integration"] = {
                    "new_import_found": new_import_found,
                    "old_import_found": old_import_found,
                    "migration_comments_found": "MIGRATION UPDATE" in content,
                    "integration_method": "open_tag_metadata_editor"
                    in content,
                }

            except Exception as e:
                results["rfuhub_integration"]["error"] = str(e)

        # Search for old import references in other files
        search_patterns = [
            "from tag_viewer_editor import",
            "import tag_viewer_editor",
            "tag_viewer_editor.py",
        ]

        python_files = list(self.base_dir.glob("*.py"))
        for py_file in python_files:
            if py_file.name in [
                "tag_viewer_editor_validation_script.py",
                "tag_viewer_editor.py",
            ]:
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern in search_patterns:
                    if pattern in content:
                        results["old_import_references"].append(
                            {
                                "file": str(py_file),
                                "pattern": pattern,
                                "line_numbers": [
                                    i + 1
                                    for i, line in enumerate(
                                        content.split("\n")
                                    )
                                    if pattern in line
                                ],
                            }
                        )
            except Exception as e:
                continue

        return results

    def test_integration_with_rfuhub(self) -> Dict[str, Any]:
        """Test integration functionality with RFU Hub."""
        print("🔗 Testing RFU Hub integration...")

        results = {
            "import_test": {},
            "method_availability": {},
            "error_handling": {},
        }

        try:
            # Test the import that RFU Hub uses
            sys.path.insert(0, str(self.base_dir))
            from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor

            results["import_test"] = {"success": True, "class_available": True}

            # Test method availability
            required_methods = ["__init__", "show", "close"]
            available_methods = []
            missing_methods = []

            for method in required_methods:
                if hasattr(TagViewerEditor, method):
                    available_methods.append(method)
                else:
                    missing_methods.append(method)

            results["method_availability"] = {
                "available_methods": available_methods,
                "missing_methods": missing_methods,
                "all_required_present": len(missing_methods) == 0,
            }

        except Exception as e:
            results["import_test"] = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        finally:
            if str(self.base_dir) in sys.path:
                sys.path.remove(str(self.base_dir))

        return results

    def verify_backup_system(self) -> Dict[str, Any]:
        """Verify backup system integrity and restoration capability."""
        print("💾 Verifying backup system...")

        results = {
            "backup_structure": {},
            "manifest_validation": {},
            "restoration_capability": {},
        }

        backup_dir = (
            self.base_dir
            / "backup/tag_viewer_editor_migration/2025-01-27_14-16-46"
        )

        # Check backup structure
        expected_files = [
            "tag_viewer_editor.py",
            "tag_viewer_editor.ui",
            "backup_manifest.txt",
        ]
        results["backup_structure"] = {
            "backup_dir_exists": backup_dir.exists(),
            "expected_files": {},
        }

        for file_name in expected_files:
            file_path = backup_dir / file_name
            results["backup_structure"]["expected_files"][file_name] = {
                "exists": file_path.exists(),
                "readable": file_path.exists()
                and os.access(file_path, os.R_OK),
            }

        # Validate manifest
        manifest_file = backup_dir / "backup_manifest.txt"
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest_content = f.read()

                results["manifest_validation"] = {
                    "contains_timestamp": "2025-01-27_14-16-46"
                    in manifest_content,
                    "contains_file_info": "tag_viewer_editor.py"
                    in manifest_content,
                    "contains_checksums": "SHA256" in manifest_content,
                    "contains_rollback_instructions": "ROLLBACK INSTRUCTIONS"
                    in manifest_content,
                }
            except Exception as e:
                results["manifest_validation"]["error"] = str(e)

        # Test restoration capability (check if backup_restore.py exists)
        restore_script = self.base_dir / "backup_restore.py"
        results["restoration_capability"] = {
            "restore_script_exists": restore_script.exists(),
            "restore_script_readable": restore_script.exists()
            and os.access(restore_script, os.R_OK),
        }

        return results

    def analyze_legacy_files(self) -> Dict[str, Any]:
        """Analyze legacy files in root directory."""
        print("📁 Analyzing legacy files...")

        results = {
            "legacy_file_analysis": {},
            "safety_assessment": {},
            "cleanup_recommendations": [],
        }

        legacy_files = ["tag_viewer_editor.py", "tag_viewer_editor.ui"]
        file_info = self.validation_results["file_structure"]

        for file_name in legacy_files:
            file_key = (
                f"legacy_{file_name.split('.')[1]}"  # legacy_py or legacy_ui
            )
            legacy_info = file_info.get(file_key, {})

            if legacy_info.get("exists"):
                # Compare with migrated version
                migrated_key = f"migrated_{file_name.split('.')[1]}"
                migrated_info = file_info.get(migrated_key, {})

                analysis = {
                    "size_bytes": legacy_info.get("size"),
                    "checksum": legacy_info.get("checksum"),
                    "identical_to_migrated": False,
                    "identical_to_backup": False,
                }

                if migrated_info.get("exists"):
                    analysis["identical_to_migrated"] = legacy_info.get(
                        "checksum"
                    ) == migrated_info.get("checksum")

                backup_key = f"backup_{file_name.split('.')[1]}"
                backup_info = file_info.get(backup_key, {})
                if backup_info.get("exists"):
                    analysis["identical_to_backup"] = legacy_info.get(
                        "checksum"
                    ) == backup_info.get("checksum")

                results["legacy_file_analysis"][file_name] = analysis

        # Safety assessment
        all_legacy_identical_to_backup = all(
            info.get("identical_to_backup", False)
            for info in results["legacy_file_analysis"].values()
        )

        migration_successful = all(
            self.validation_results["file_structure"]
            .get(f"migrated_{ext}", {})
            .get("exists", False)
            for ext in ["py", "ui"]
        )

        results["safety_assessment"] = {
            "all_legacy_identical_to_backup": all_legacy_identical_to_backup,
            "migration_successful": migration_successful,
            "safe_to_remove_legacy": all_legacy_identical_to_backup
            and migration_successful,
        }

        # Cleanup recommendations
        if results["safety_assessment"]["safe_to_remove_legacy"]:
            results["cleanup_recommendations"].append(
                "✅ Legacy files are identical to backup and migration is successful. "
                "Legacy files can be safely removed."
            )
        else:
            results["cleanup_recommendations"].append(
                "⚠️ Legacy files should be retained until further validation. "
                "Differences detected or migration issues found."
            )

        return results

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests and compile results."""
        print(
            "🚀 Starting comprehensive tag_viewer_editor migration validation...\n"
        )

        # Run all validation steps
        self.validation_results["file_structure"] = (
            self.validate_file_structure()
        )
        self.validation_results["checksums"] = (
            self.validate_migration_integrity()
        )
        self.validation_results["pyqt5_compatibility"] = (
            self.test_pyqt5_compatibility()
        )
        self.validation_results["import_validation"] = (
            self.validate_import_statements()
        )
        self.validation_results["integration_tests"] = (
            self.test_integration_with_rfuhub()
        )
        self.validation_results["backup_verification"] = (
            self.verify_backup_system()
        )
        self.validation_results["legacy_analysis"] = (
            self.analyze_legacy_files()
        )

        # Compile issues and recommendations
        self._compile_issues_and_recommendations()

        return self.validation_results

    def _compile_issues_and_recommendations(self):
        """Compile issues found and recommendations."""
        issues = []
        recommendations = []

        # Check for critical issues
        file_structure = self.validation_results["file_structure"]
        if not file_structure.get("migrated_py", {}).get("exists"):
            issues.append("❌ CRITICAL: Migrated Python file not found")
        if not file_structure.get("migrated_ui", {}).get("exists"):
            issues.append("❌ CRITICAL: Migrated UI file not found")

        # Check PyQt5 compatibility
        pyqt5_compat = self.validation_results["pyqt5_compatibility"]
        if not pyqt5_compat.get("pyqt5_available"):
            issues.append("❌ CRITICAL: PyQt5 not available for testing")
        elif (
            not pyqt5_compat.get("import_tests", {})
            .get("direct_import", {})
            .get("success")
        ):
            issues.append(
                "❌ CRITICAL: Cannot import migrated TagViewerEditor class"
            )

        # Check integration
        integration = self.validation_results["integration_tests"]
        if not integration.get("import_test", {}).get("success"):
            issues.append("❌ CRITICAL: RFU Hub integration test failed")

        # Check backup system
        backup = self.validation_results["backup_verification"]
        if not backup.get("backup_structure", {}).get("backup_dir_exists"):
            issues.append("⚠️ WARNING: Backup directory not found")

        # Add recommendations based on findings
        legacy_analysis = self.validation_results.get("legacy_analysis", {})
        if legacy_analysis.get("safety_assessment", {}).get(
            "safe_to_remove_legacy"
        ):
            recommendations.append("✅ Legacy files can be safely removed")
        else:
            recommendations.append(
                "⚠️ Retain legacy files until issues are resolved"
            )

        if not issues:
            recommendations.append(
                "🎉 Migration validation successful - all tests passed!"
            )

        self.validation_results["issues_found"] = issues
        self.validation_results["recommendations"] = recommendations

    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report = []
        report.append("=" * 80)
        report.append("TAG VIEWER EDITOR MIGRATION VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {self._get_timestamp()}")
        report.append(
            f"Validation Script: tag_viewer_editor_validation_script.py"
        )
        report.append("")

        # Executive Summary
        report.append("📋 EXECUTIVE SUMMARY")
        report.append("-" * 40)
        issues = self.validation_results.get("issues_found", [])
        if not issues:
            report.append("✅ VALIDATION STATUS: PASSED")
            report.append(
                "✅ All migration validation tests completed successfully"
            )
        else:
            report.append("❌ VALIDATION STATUS: ISSUES FOUND")
            report.append(f"❌ {len(issues)} issue(s) require attention")
        report.append("")

        # Issues Found
        if issues:
            report.append("🚨 ISSUES FOUND")
            report.append("-" * 40)
            for issue in issues:
                report.append(f"  {issue}")
            report.append("")

        # Recommendations
        recommendations = self.validation_results.get("recommendations", [])
        if recommendations:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in recommendations:
                report.append(f"  {rec}")
            report.append("")

        # Detailed Results
        report.append("📊 DETAILED VALIDATION RESULTS")
        report.append("-" * 40)

        # File Structure
        report.append("\n1. FILE STRUCTURE VALIDATION")
        file_structure = self.validation_results.get("file_structure", {})
        for file_key, info in file_structure.items():
            status = "✅" if info.get("exists") else "❌"
            size = info.get("size", "N/A")
            report.append(f"   {status} {file_key}: {size} bytes")

        # Migration Integrity
        report.append("\n2. MIGRATION INTEGRITY")
        checksums = self.validation_results.get("checksums", {})
        for desc, result in checksums.items():
            if "error" in result:
                report.append(f"   ❌ {desc}: {result['error']}")
            else:
                status = "✅" if result.get("match") else "❌"
                report.append(
                    f"   {status} {desc}: Checksums {'match' if result.get('match') else 'differ'}"
                )

        # PyQt5 Compatibility
        report.append("\n3. PYQT5 COMPATIBILITY")
        pyqt5 = self.validation_results.get("pyqt5_compatibility", {})
        pyqt5_status = "✅" if pyqt5.get("pyqt5_available") else "❌"
        report.append(
            f"   {pyqt5_status} PyQt5 Available: {pyqt5.get('pyqt5_available')}"
        )

        import_test = pyqt5.get("import_tests", {}).get("direct_import", {})
        import_status = "✅" if import_test.get("success") else "❌"
        report.append(
            f"   {import_status} Import Test: {import_test.get('success', False)}"
        )

        ui_test = pyqt5.get("ui_loading_test", {})
        ui_status = "✅" if ui_test.get("success") else "❌"
        report.append(
            f"   {ui_status} UI Loading: {ui_test.get('success', False)}"
        )

        # Integration Tests
        report.append("\n4. INTEGRATION TESTS")
        integration = self.validation_results.get("integration_tests", {})
        int_status = (
            "✅" if integration.get("import_test", {}).get("success") else "❌"
        )
        report.append(
            f"   {int_status} RFU Hub Integration: {integration.get('import_test', {}).get('success', False)}"
        )

        # Backup Verification
        report.append("\n5. BACKUP VERIFICATION")
        backup = self.validation_results.get("backup_verification", {})
        backup_status = (
            "✅"
            if backup.get("backup_structure", {}).get("backup_dir_exists")
            else "❌"
        )
        report.append(
            f"   {backup_status} Backup Directory: {backup.get('backup_structure', {}).get('backup_dir_exists', False)}"
        )

        # Legacy File Analysis
        report.append("\n6. LEGACY FILE ANALYSIS")
        legacy = self.validation_results.get("legacy_analysis", {})
        safe_remove = legacy.get("safety_assessment", {}).get(
            "safe_to_remove_legacy", False
        )
        legacy_status = "✅" if safe_remove else "⚠️"
        report.append(
            f"   {legacy_status} Safe to Remove Legacy: {safe_remove}"
        )

        report.append("")
        report.append("=" * 80)
        report.append("END OF VALIDATION REPORT")
        report.append("=" * 80)

        return "\n".join(report)

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")


def main():
    """Main function to run the validation."""
    validator = TagViewerEditorValidator()

    try:
        # Run comprehensive validation
        results = validator.run_comprehensive_validation()

        # Generate and display report
        report = validator.generate_report()
        print("\n" + report)

        # Save report to file
        report_file = Path("tag_viewer_editor_validation_report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 Full report saved to: {report_file}")

        # Return exit code based on validation results
        issues = results.get("issues_found", [])
        critical_issues = [issue for issue in issues if "CRITICAL" in issue]

        if critical_issues:
            print(
                f"\n❌ Validation failed with {len(critical_issues)} critical issue(s)"
            )
            return 1
        elif issues:
            print(f"\n⚠️ Validation completed with {len(issues)} warning(s)")
            return 0
        else:
            print("\n✅ Validation completed successfully - no issues found")
            return 0

    except Exception as e:
        print(f"\n💥 Validation script failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
