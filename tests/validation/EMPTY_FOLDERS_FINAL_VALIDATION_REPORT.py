#!/usr/bin/env python3
"""
EMPTY FOLDERS MIGRATION - FINAL VALIDATION REPORT
==================================================

This script performs comprehensive final validation of the empty folders migration project
and generates a detailed production readiness assessment.

Author: Debug Mode Validation System
Date: 2025-07-26
Status: COMPREHENSIVE FINAL VALIDATION
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime


class EmptyFoldersMigrationValidator:
    """Comprehensive validator for the empty folders migration project."""

    def __init__(self):
        self.validation_results = {}
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []
        self.production_ready = True

    def validate_file_structure(self) -> Dict[str, Any]:
        """Validate file structure and locations."""
        print("🔍 VALIDATING FILE STRUCTURE...")

        results = {"status": "PASSED", "details": {}, "issues": []}

        # Check migrated files exist
        required_files = [
            "file_utilities_1/empty_folders.py",
            "file_utilities_1/empty_folders.ui",
            "file_utilities_1/empty_folder_files_md",
            "file_utilities_1/__init__.py",
        ]

        for file_path in required_files:
            if Path(file_path).exists():
                results["details"][file_path] = "✅ EXISTS"
                print(f"  ✅ {file_path}")
            else:
                results["details"][file_path] = "❌ MISSING"
                results["issues"].append(f"Missing required file: {file_path}")
                results["status"] = "FAILED"
                self.critical_issues.append(
                    f"Critical file missing: {file_path}"
                )
                print(f"  ❌ {file_path}")

        # Check original files were removed
        original_files = ["empty_folders.py", "empty_folders.ui"]
        for file_path in original_files:
            if not Path(file_path).exists():
                results["details"][
                    f"removed_{file_path}"
                ] = "✅ PROPERLY REMOVED"
                print(f"  ✅ Original {file_path} properly removed")
            else:
                results["details"][f"removed_{file_path}"] = "⚠️ STILL EXISTS"
                results["issues"].append(
                    f"Original file still exists: {file_path}"
                )
                self.warnings.append(
                    f"Original file not cleaned up: {file_path}"
                )
                print(f"  ⚠️ Original {file_path} still exists")

        return results

    def validate_imports_and_exports(self) -> Dict[str, Any]:
        """Validate import statements and package exports."""
        print("\n🔍 VALIDATING IMPORTS AND EXPORTS...")

        results = {"status": "PASSED", "details": {}, "issues": []}

        # Check package __init__.py exports
        try:
            init_file = Path("file_utilities_1/__init__.py")
            if init_file.exists():
                content = init_file.read_text()
                if "EmptyFoldersWindow" in content:
                    results["details"]["package_export"] = "✅ EXPORTED"
                    print("  ✅ EmptyFoldersWindow exported in package")
                else:
                    results["details"]["package_export"] = "❌ NOT EXPORTED"
                    results["issues"].append(
                        "EmptyFoldersWindow not exported in package"
                    )
                    results["status"] = "FAILED"
                    self.critical_issues.append("Package export missing")
                    print("  ❌ EmptyFoldersWindow not exported")
            else:
                results["status"] = "FAILED"
                self.critical_issues.append("Package __init__.py missing")
        except Exception as e:
            results["issues"].append(f"Error checking package exports: {e}")
            results["status"] = "FAILED"

        # Check main module imports
        try:
            main_file = Path("file_utilities_1/empty_folders.py")
            if main_file.exists():
                content = main_file.read_text()

                # Check for BaseWindow import
                if "from gui.common.base_window import BaseWindow" in content:
                    results["details"]["base_window_import"] = "✅ CORRECT"
                    print("  ✅ BaseWindow import correct")
                else:
                    results["details"]["base_window_import"] = "❌ INCORRECT"
                    results["issues"].append(
                        "BaseWindow import missing or incorrect"
                    )
                    self.warnings.append("BaseWindow import issue")
                    print("  ❌ BaseWindow import issue")

                # Check for UI file loading
                if "uic.loadUi" in content or "_UI_FILE" in content:
                    results["details"]["ui_loading"] = "✅ UI FILE PATTERN"
                    print("  ✅ UI file loading pattern detected")
                else:
                    results["details"]["ui_loading"] = "⚠️ PATTERN NOT DETECTED"
                    self.warnings.append(
                        "UI file loading pattern not clearly detected"
                    )
                    print("  ⚠️ UI file loading pattern unclear")

        except Exception as e:
            results["issues"].append(f"Error checking main module: {e}")

        return results

    def validate_integration_points(self) -> Dict[str, Any]:
        """Validate integration points that need updating."""
        print("\n🔍 VALIDATING INTEGRATION POINTS...")

        results = {
            "status": "NEEDS_UPDATES",
            "details": {},
            "issues": [],
            "required_updates": [],
        }

        # Check RFU Hub integration
        try:
            rfuhub_file = Path("rfuhub.py")
            if rfuhub_file.exists():
                content = rfuhub_file.read_text()

                if "from empty_folders import EmptyFoldersGUI" in content:
                    results["details"][
                        "rfuhub_integration"
                    ] = "❌ NEEDS UPDATE"
                    results["required_updates"].append(
                        {
                            "file": "rfuhub.py",
                            "line_approx": 479,
                            "current": "from empty_folders import EmptyFoldersGUI",
                            "required": "from file_utilities_1.empty_folders import EmptyFoldersWindow",
                            "priority": "HIGH",
                        }
                    )
                    print("  ❌ RFU Hub needs import update")
                else:
                    results["details"][
                        "rfuhub_integration"
                    ] = "✅ UPDATED OR N/A"
                    print("  ✅ RFU Hub integration appears updated")

        except Exception as e:
            results["issues"].append(f"Error checking RFU Hub: {e}")

        # Check test suite
        try:
            test_file = Path("tests/test_empty_folders.py")
            if test_file.exists():
                content = test_file.read_text()

                if "from empty_folders import" in content:
                    results["details"]["test_suite"] = "❌ NEEDS UPDATE"
                    results["required_updates"].append(
                        {
                            "file": "tests/test_empty_folders.py",
                            "line_approx": 5,
                            "current": "from empty_folders import EmptyFolderLogic, EmptyFolderCleaner",
                            "required": "from file_utilities_1.empty_folders import EmptyFolderLogic",
                            "priority": "MEDIUM",
                        }
                    )
                    print("  ❌ Test suite needs import update")
                else:
                    results["details"]["test_suite"] = "✅ UPDATED OR N/A"
                    print("  ✅ Test suite appears updated")

        except Exception as e:
            results["issues"].append(f"Error checking test suite: {e}")

        return results

    def validate_ui_architecture(self) -> Dict[str, Any]:
        """Validate UI architecture and file structure."""
        print("\n🔍 VALIDATING UI ARCHITECTURE...")

        results = {"status": "PASSED", "details": {}, "issues": []}

        # Check UI file format
        try:
            ui_file = Path("file_utilities_1/empty_folders.ui")
            if ui_file.exists():
                content = ui_file.read_text()

                if content.startswith("<?xml"):
                    results["details"]["ui_format"] = "✅ VALID XML"
                    print("  ✅ UI file is valid XML format")
                else:
                    results["details"]["ui_format"] = "❌ INVALID FORMAT"
                    results["issues"].append("UI file is not valid XML")
                    results["status"] = "FAILED"
                    print("  ❌ UI file format invalid")

                # Check for required UI elements
                required_elements = [
                    "pathInput",
                    "browseButton",
                    "scanButton",
                    "stopButton",
                    "folderList",
                    "selectAllButton",
                    "unselectAllButton",
                    "deleteButton",
                    "statusLabel",
                ]

                missing_elements = []
                for element in required_elements:
                    if f'name="{element}"' in content:
                        print(f"    ✅ {element}")
                    else:
                        missing_elements.append(element)
                        print(f"    ❌ {element}")

                if missing_elements:
                    results["details"][
                        "ui_elements"
                    ] = f"❌ MISSING: {missing_elements}"
                    results["issues"].append(
                        f"Missing UI elements: {missing_elements}"
                    )
                    results["status"] = "FAILED"
                else:
                    results["details"]["ui_elements"] = "✅ ALL PRESENT"

        except Exception as e:
            results["issues"].append(f"Error checking UI file: {e}")
            results["status"] = "FAILED"

        return results

    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness and accuracy."""
        print("\n🔍 VALIDATING DOCUMENTATION...")

        results = {"status": "PASSED", "details": {}, "issues": []}

        # Check for migration documentation
        doc_files = [
            "EMPTY_FOLDERS_MIGRATION_VALIDATION_REPORT.md",
            "EMPTY_FOLDERS_MIGRATION_COMPREHENSIVE_DOCUMENTATION.md",
        ]

        for doc_file in doc_files:
            if Path(doc_file).exists():
                results["details"][doc_file] = "✅ EXISTS"
                print(f"  ✅ {doc_file}")
            else:
                results["details"][doc_file] = "❌ MISSING"
                results["issues"].append(f"Missing documentation: {doc_file}")
                self.warnings.append(f"Documentation missing: {doc_file}")
                print(f"  ❌ {doc_file}")

        # Check original documentation preservation
        if Path("file_utilities_1/empty_folder_files_md").exists():
            results["details"]["original_docs"] = "✅ PRESERVED"
            print("  ✅ Original documentation preserved")
        else:
            results["details"]["original_docs"] = "❌ MISSING"
            results["issues"].append("Original documentation not preserved")
            self.warnings.append("Original documentation missing")
            print("  ❌ Original documentation missing")

        return results

    def assess_production_readiness(self) -> Dict[str, Any]:
        """Assess overall production readiness."""
        print("\n🎯 ASSESSING PRODUCTION READINESS...")

        # Determine readiness based on critical issues
        if self.critical_issues:
            self.production_ready = False
            status = "❌ NOT READY"
            print(f"  {status} - Critical issues found")
        elif self.warnings:
            status = "⚠️ READY WITH UPDATES"
            print(f"  {status} - Minor updates needed")
        else:
            status = "✅ FULLY READY"
            print(f"  {status} - No issues found")

        readiness = {
            "status": status,
            "production_ready": self.production_ready,
            "critical_issues_count": len(self.critical_issues),
            "warnings_count": len(self.warnings),
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }

        return readiness

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        print("\n💡 GENERATING RECOMMENDATIONS...")

        recommendations = []

        # Critical issue recommendations
        if self.critical_issues:
            recommendations.append(
                "🚨 CRITICAL: Address all critical issues before deployment"
            )
            for issue in self.critical_issues:
                recommendations.append(f"   - {issue}")

        # Integration update recommendations
        if any(
            "NEEDS UPDATE" in str(result)
            for result in self.validation_results.values()
        ):
            recommendations.append(
                "🔧 UPDATE REQUIRED: Update integration points"
            )
            recommendations.append("   - Update rfuhub.py import statements")
            recommendations.append("   - Update test suite import statements")
            recommendations.append(
                "   - Verify all references point to new locations"
            )

        # General recommendations
        recommendations.extend(
            [
                "✅ VALIDATION: Run integration tests when Python environment available",
                "✅ TESTING: Perform user acceptance testing of UI functionality",
                "✅ MONITORING: Monitor performance after deployment",
                "✅ BACKUP: Ensure backup of original files before final cleanup",
            ]
        )

        self.recommendations = recommendations
        return recommendations

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        print("=" * 80)
        print("EMPTY FOLDERS MIGRATION - FINAL VALIDATION")
        print("=" * 80)
        print(f"Validation Time: {datetime.now().isoformat()}")
        print(f"Working Directory: {os.getcwd()}")
        print("=" * 80)

        # Run all validation tests
        self.validation_results = {
            "file_structure": self.validate_file_structure(),
            "imports_exports": self.validate_imports_and_exports(),
            "integration_points": self.validate_integration_points(),
            "ui_architecture": self.validate_ui_architecture(),
            "documentation": self.validate_documentation(),
        }

        # Generate recommendations
        self.generate_recommendations()

        # Assess production readiness
        readiness = self.assess_production_readiness()

        # Compile final report
        final_report = {
            "validation_timestamp": datetime.now().isoformat(),
            "validation_results": self.validation_results,
            "production_readiness": readiness,
            "recommendations": self.recommendations,
            "summary": self.generate_summary(),
        }

        return final_report

    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        total_tests = len(self.validation_results)
        passed_tests = sum(
            1
            for result in self.validation_results.values()
            if result.get("status") == "PASSED"
        )

        return {
            "total_validation_areas": total_tests,
            "passed_validations": passed_tests,
            "failed_validations": total_tests - passed_tests,
            "critical_issues": len(self.critical_issues),
            "warnings": len(self.warnings),
            "overall_status": (
                "PASSED" if self.production_ready else "NEEDS_ATTENTION"
            ),
        }

    def print_final_report(self, report: Dict[str, Any]) -> None:
        """Print formatted final report."""
        print("\n" + "=" * 80)
        print("FINAL VALIDATION REPORT")
        print("=" * 80)

        # Summary
        summary = report["summary"]
        print(f"📊 VALIDATION SUMMARY:")
        print(f"   Total Areas Tested: {summary['total_validation_areas']}")
        print(f"   Passed: {summary['passed_validations']}")
        print(f"   Failed: {summary['failed_validations']}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        print(f"   Warnings: {summary['warnings']}")
        print(f"   Overall Status: {summary['overall_status']}")

        # Production Readiness
        readiness = report["production_readiness"]
        print(f"\n🎯 PRODUCTION READINESS: {readiness['status']}")

        if readiness["critical_issues"]:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in readiness["critical_issues"]:
                print(f"   - {issue}")

        if readiness["warnings"]:
            print("\n⚠️ WARNINGS:")
            for warning in readiness["warnings"]:
                print(f"   - {warning}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   {rec}")

        # Integration Updates Needed
        integration_result = report["validation_results"].get(
            "integration_points", {}
        )
        if integration_result.get("required_updates"):
            print("\n🔧 REQUIRED INTEGRATION UPDATES:")
            for update in integration_result["required_updates"]:
                print(
                    f"   📁 {update['file']} (Line ~{update['line_approx']}) - Priority: {update['priority']}"
                )
                print(f"      Current: {update['current']}")
                print(f"      Required: {update['required']}")
                print()

        print("=" * 80)

        # Final verdict
        if readiness["production_ready"]:
            print("🎉 MIGRATION VALIDATION SUCCESSFUL!")
            print(
                "   The empty folders migration is ready for production deployment."
            )
        else:
            print("⚠️ MIGRATION VALIDATION INCOMPLETE!")
            print(
                "   Critical issues must be resolved before production deployment."
            )

        print("=" * 80)


def main():
    """Main validation function."""
    validator = EmptyFoldersMigrationValidator()
    report = validator.run_full_validation()
    validator.print_final_report(report)

    # Save report to file
    report_file = "EMPTY_FOLDERS_FINAL_VALIDATION_RESULTS.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Return exit code based on validation results
    return 0 if report["production_readiness"]["production_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
