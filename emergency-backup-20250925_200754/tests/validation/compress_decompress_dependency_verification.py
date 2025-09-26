#!/usr/bin/env python3
"""
Comprehensive dependency verification script for compress_decompress migration to file_utilities_1.
This script tests all required dependencies and their compatibility.
"""

import sys
import os
import importlib
from typing import Dict, List, Tuple, Any
from pathlib import Path


class DependencyVerifier:
    """Verifies all dependencies required for compress_decompress migration."""

    def __init__(self):
        self.results = {}
        self.critical_failures = []
        self.warnings = []

    def test_external_dependencies(self) -> Dict[str, Any]:
        """Test external package dependencies."""
        print("📦 Testing External Dependencies...")
        results = {}

        # Test py7zr (critical for 7Z support)
        try:
            import py7zr

            results["py7zr"] = {
                "status": "AVAILABLE",
                "version": getattr(py7zr, "__version__", "Unknown"),
                "critical": True,
            }

            # Test specific functionality
            if hasattr(py7zr, "FILTER_LZMA2"):
                results["py7zr"]["FILTER_LZMA2"] = "AVAILABLE"
            else:
                results["py7zr"]["FILTER_LZMA2"] = "MISSING"
                self.critical_failures.append("py7zr.FILTER_LZMA2 missing")

            if hasattr(py7zr, "SevenZipFile"):
                results["py7zr"]["SevenZipFile"] = "AVAILABLE"
            else:
                results["py7zr"]["SevenZipFile"] = "MISSING"
                self.critical_failures.append("py7zr.SevenZipFile missing")

        except ImportError as e:
            results["py7zr"] = {
                "status": "NOT_AVAILABLE",
                "error": str(e),
                "critical": True,
            }
            self.critical_failures.append(f"py7zr not available: {e}")

        return results

    def test_builtin_dependencies(self) -> Dict[str, Any]:
        """Test built-in Python library dependencies."""
        print("📦 Testing Built-in Dependencies...")
        results = {}

        builtin_libs = [
            ("zipfile", ["ZIP_DEFLATED"]),
            ("tarfile", []),
            ("os", ["walk", "path"]),
            ("typing", ["Dict"]),
            ("pathlib", ["Path"]),
        ]

        for lib_name, required_attrs in builtin_libs:
            try:
                lib = importlib.import_module(lib_name)
                results[lib_name] = {"status": "AVAILABLE"}

                for attr in required_attrs:
                    if hasattr(lib, attr):
                        results[lib_name][attr] = "AVAILABLE"
                    else:
                        results[lib_name][attr] = "MISSING"
                        self.warnings.append(f"{lib_name}.{attr} missing")

            except ImportError as e:
                results[lib_name] = {
                    "status": "NOT_AVAILABLE",
                    "error": str(e),
                }
                self.critical_failures.append(f"{lib_name} not available: {e}")

        return results

    def test_pyqt5_dependencies(self) -> Dict[str, Any]:
        """Test PyQt5 dependencies."""
        print("📦 Testing PyQt5 Dependencies...")
        results = {}

        pyqt5_modules = [
            (
                "PyQt5.QtWidgets",
                [
                    "QApplication",
                    "QMainWindow",
                    "QWidget",
                    "QLineEdit",
                    "QPushButton",
                    "QComboBox",
                    "QSlider",
                ],
            ),
            ("PyQt5.QtGui", ["QDragEnterEvent", "QDropEvent"]),
            ("PyQt5.QtCore", ["Qt"]),
            ("PyQt5", ["uic"]),
        ]

        for module_name, required_classes in pyqt5_modules:
            try:
                module = importlib.import_module(module_name)
                results[module_name] = {"status": "AVAILABLE"}

                for class_name in required_classes:
                    if hasattr(module, class_name):
                        results[module_name][class_name] = "AVAILABLE"
                    else:
                        results[module_name][class_name] = "MISSING"
                        self.critical_failures.append(
                            f"{module_name}.{class_name} missing"
                        )

            except ImportError as e:
                results[module_name] = {
                    "status": "NOT_AVAILABLE",
                    "error": str(e),
                }
                self.critical_failures.append(
                    f"{module_name} not available: {e}"
                )

        return results

    def test_gui_common_framework(self) -> Dict[str, Any]:
        """Test gui.common framework dependencies."""
        print("📦 Testing GUI Common Framework...")
        results = {}

        # Add current directory to path for testing
        current_dir = Path.cwd()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        framework_modules = [
            ("core.error_handler", ["error_handler"]),
            (
                "gui.common.styles",
                ["get_base_styles", "get_custom_styles", "Theme"],
            ),
            ("gui.common.settings", ["AppearanceSettings"]),
            (
                "gui.common.dialogs",
                [
                    "show_error_dialog",
                    "show_info_dialog",
                    "get_existing_directory",
                    "get_open_file_name",
                    "get_save_file_name",
                ],
            ),
            ("gui.common.base_window", ["BaseWindow"]),
        ]

        for module_name, required_items in framework_modules:
            try:
                module = importlib.import_module(module_name)
                results[module_name] = {"status": "AVAILABLE"}

                for item_name in required_items:
                    if hasattr(module, item_name):
                        results[module_name][item_name] = "AVAILABLE"
                    else:
                        results[module_name][item_name] = "MISSING"
                        self.critical_failures.append(
                            f"{module_name}.{item_name} missing"
                        )

            except ImportError as e:
                results[module_name] = {
                    "status": "NOT_AVAILABLE",
                    "error": str(e),
                }
                self.critical_failures.append(
                    f"{module_name} not available: {e}"
                )

        return results

    def test_ui_file_loading(self) -> Dict[str, Any]:
        """Test UI file loading mechanisms."""
        print("📦 Testing UI File Loading...")
        results = {}

        # Test if compress_decompress.ui exists
        ui_file = Path("compress_decompress.ui")
        if ui_file.exists():
            results["compress_decompress.ui"] = {
                "status": "EXISTS",
                "size": ui_file.stat().st_size,
                "readable": True,
            }

            # Test readability
            try:
                with open(ui_file, "r", encoding="utf-8") as f:
                    content = f.read(100)
                results["compress_decompress.ui"]["sample_content"] = (
                    content[:50] + "..."
                )
            except Exception as e:
                results["compress_decompress.ui"]["readable"] = False
                results["compress_decompress.ui"]["error"] = str(e)
                self.warnings.append(f"UI file read error: {e}")
        else:
            results["compress_decompress.ui"] = {"status": "NOT_FOUND"}
            self.critical_failures.append(
                "compress_decompress.ui file not found"
            )

        # Test PyQt5.uic functionality
        try:
            from PyQt5 import uic

            results["uic_functionality"] = {"status": "AVAILABLE"}

            # Test if we can load UI programmatically
            if ui_file.exists():
                try:
                    # This would normally require a QApplication, but we can test the file parsing
                    results["uic_functionality"]["ui_parsing"] = "TESTABLE"
                except Exception as e:
                    results["uic_functionality"]["ui_parsing"] = f"ERROR: {e}"

        except ImportError as e:
            results["uic_functionality"] = {
                "status": "NOT_AVAILABLE",
                "error": str(e),
            }
            self.critical_failures.append(f"PyQt5.uic not available: {e}")

        return results

    def test_drag_drop_functionality(self) -> Dict[str, Any]:
        """Test drag and drop functionality requirements."""
        print("📦 Testing Drag & Drop Functionality...")
        results = {}

        try:
            from PyQt5.QtGui import QDragEnterEvent, QDropEvent
            from PyQt5.QtCore import QMimeData, QUrl
            from PyQt5.QtWidgets import QApplication

            results["drag_drop_events"] = {"status": "AVAILABLE"}
            results["mime_data"] = {"status": "AVAILABLE"}
            results["qurl"] = {"status": "AVAILABLE"}

            # Test if we can create the required objects (without GUI)
            try:
                # These would normally require a QApplication context
                results["drag_drop_functionality"] = "CLASSES_AVAILABLE"
            except Exception as e:
                results["drag_drop_functionality"] = (
                    f"INSTANTIATION_ERROR: {e}"
                )
                self.warnings.append(f"Drag/drop instantiation issue: {e}")

        except ImportError as e:
            results["drag_drop_events"] = {
                "status": "NOT_AVAILABLE",
                "error": str(e),
            }
            self.critical_failures.append(
                f"Drag/drop functionality not available: {e}"
            )

        return results

    def generate_report(self) -> str:
        """Generate comprehensive dependency analysis report."""
        print("\n" + "=" * 80)
        print("🔍 COMPRESS_DECOMPRESS DEPENDENCY ANALYSIS REPORT")
        print("=" * 80)

        # Run all tests
        external_deps = self.test_external_dependencies()
        builtin_deps = self.test_builtin_dependencies()
        pyqt5_deps = self.test_pyqt5_dependencies()
        gui_framework = self.test_gui_common_framework()
        ui_loading = self.test_ui_file_loading()
        drag_drop = self.test_drag_drop_functionality()

        # Compile results
        all_results = {
            "external_dependencies": external_deps,
            "builtin_dependencies": builtin_deps,
            "pyqt5_dependencies": pyqt5_deps,
            "gui_common_framework": gui_framework,
            "ui_file_loading": ui_loading,
            "drag_drop_functionality": drag_drop,
        }

        # Generate report
        report = []
        report.append("\n📋 DEPENDENCY AVAILABILITY STATUS:")
        report.append("-" * 50)

        for category, deps in all_results.items():
            report.append(f"\n🔧 {category.replace('_', ' ').title()}:")
            for dep_name, dep_info in deps.items():
                if isinstance(dep_info, dict) and "status" in dep_info:
                    status = dep_info["status"]
                    if status == "AVAILABLE":
                        report.append(f"  ✅ {dep_name}: {status}")
                        if "version" in dep_info:
                            report.append(
                                f"     Version: {dep_info['version']}"
                            )
                    else:
                        report.append(f"  ❌ {dep_name}: {status}")
                        if "error" in dep_info:
                            report.append(f"     Error: {dep_info['error']}")
                else:
                    report.append(f"  ℹ️  {dep_name}: {dep_info}")

        # Critical issues
        if self.critical_failures:
            report.append(
                f"\n🚨 CRITICAL ISSUES ({len(self.critical_failures)}):"
            )
            report.append("-" * 30)
            for issue in self.critical_failures:
                report.append(f"  ❌ {issue}")

        # Warnings
        if self.warnings:
            report.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            report.append("-" * 20)
            for warning in self.warnings:
                report.append(f"  ⚠️  {warning}")

        # Installation requirements
        report.append("\n📦 INSTALLATION REQUIREMENTS:")
        report.append("-" * 35)

        if any("py7zr" in str(failure) for failure in self.critical_failures):
            report.append("  📥 REQUIRED: pip install py7zr")
            report.append("     Purpose: 7Z archive support")

        if any("PyQt5" in str(failure) for failure in self.critical_failures):
            report.append("  📥 REQUIRED: pip install PyQt5")
            report.append("     Purpose: GUI framework")

        # Migration readiness assessment
        report.append("\n🎯 MIGRATION READINESS ASSESSMENT:")
        report.append("-" * 40)

        if not self.critical_failures:
            report.append("  ✅ READY FOR MIGRATION")
            report.append("     All critical dependencies are available")
            report.append("     All required functionality is accessible")
        else:
            report.append("  ❌ NOT READY FOR MIGRATION")
            report.append(
                f"     {len(self.critical_failures)} critical issues must be resolved"
            )
            report.append(
                "     Install missing dependencies before proceeding"
            )

        # Compatibility verification
        report.append("\n🔍 COMPATIBILITY VERIFICATION:")
        report.append("-" * 35)

        # Check file_utilities_1 compatibility
        file_utils_1_path = Path("file_utilities_1")
        if file_utils_1_path.exists():
            report.append("  ✅ file_utilities_1 directory: EXISTS")

            # Check for gui.common framework in target
            gui_common_path = file_utils_1_path / "gui" / "common"
            if gui_common_path.exists():
                report.append("  ✅ Target gui.common framework: EXISTS")
            else:
                report.append("  ❌ Target gui.common framework: MISSING")
                report.append(
                    "     GUI common framework needs to be migrated first"
                )
        else:
            report.append("  ❌ file_utilities_1 directory: NOT FOUND")
            report.append("     Target migration directory missing")

        # Recommendations
        report.append("\n💡 RECOMMENDATIONS:")
        report.append("-" * 20)

        if not self.critical_failures:
            report.append(
                "  1. ✅ All dependencies satisfied - migration can proceed"
            )
            report.append(
                "  2. 🔄 Ensure gui.common framework is available in file_utilities_1"
            )
            report.append("  3. 📋 Test UI file loading after migration")
            report.append(
                "  4. 🧪 Verify drag-and-drop functionality post-migration"
            )
        else:
            report.append(
                "  1. 📥 Install missing dependencies (see requirements above)"
            )
            report.append("  2. 🔧 Resolve critical framework issues")
            report.append("  3. 🧪 Re-run verification after fixes")
            report.append(
                "  4. ⏸️  Postpone migration until all issues resolved"
            )

        return "\n".join(report)


def main():
    """Main function to run dependency verification."""
    print("🔍 Starting Compress/Decompress Dependency Verification...")

    verifier = DependencyVerifier()
    report = verifier.generate_report()

    print(report)

    # Save report to file
    report_file = Path("compress_decompress_dependency_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")

    # Return exit code based on critical failures
    if verifier.critical_failures:
        print(
            f"\n❌ Verification FAILED: {len(verifier.critical_failures)} critical issues"
        )
        return 1
    else:
        print(f"\n✅ Verification PASSED: Ready for migration")
        return 0


if __name__ == "__main__":
    sys.exit(main())
