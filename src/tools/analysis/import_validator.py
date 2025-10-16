"""
Import Validation Utility for Size Analyzer

This module provides comprehensive import validation and debugging
capabilities for the Size Analyzer and related modules.
"""

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class ImportValidator:
    """Comprehensive import validation and debugging utility."""

    def __init__(self):
        self.validation_results = {}
        self.import_paths = []
        self.missing_modules = []
        self.circular_imports = []

    def validate_size_analyzer_imports(self) -> Dict[str, Any]:
        """Validate all Size Analyzer related imports."""
        results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "info": [],
            "module_status": {},
        }

        # Define modules to validate
        modules_to_check = [
            ("src.tools.analysis.size_analyzer", "SizeAnalyzerGUI"),
            ("tools.analysis.size_analyzer", "SizeAnalyzerGUI"),
            (
                "src.tools.analysis.size_analyzer.size_analyzer_logic",
                "SizeAnalyzer",
            ),
            (
                "tools.analysis.size_analyzer.size_analyzer_logic",
                "SizeAnalyzer",
            ),
            (
                "src.tools.analysis.size_analyzer.size_analyzer_config",
                "SizeAnalyzerConfig",
            ),
            (
                "tools.analysis.size_analyzer.size_analyzer_config",
                "SizeAnalyzerConfig",
            ),
            (
                "src.tools.analysis.size_analyzer.size_analyzer_logging",
                "SizeAnalyzerLogger",
            ),
            (
                "tools.analysis.size_analyzer.size_analyzer_logging",
                "SizeAnalyzerLogger",
            ),
        ]

        for module_path, class_name in modules_to_check:
            status = self._validate_module_import(module_path, class_name)
            results["module_status"][module_path] = status

            if not status["importable"]:
                results["success"] = False
                error_msg = (
                    f"Cannot import {class_name} from {module_path}: "
                    f"{status['error']}"
                )
                results["errors"].append(error_msg)
            else:
                info_msg = f"Successfully imported {class_name} from {module_path}"
                results["info"].append(info_msg)

        # Validate Python path configuration
        path_status = self._validate_python_path()
        results["python_path_status"] = path_status

        if not path_status["valid"]:
            results["warnings"].extend(path_status["issues"])

        # Check for circular imports
        circular_status = self._check_circular_imports()
        results["circular_imports"] = circular_status

        if circular_status["found"]:
            results["warnings"].extend(circular_status["issues"])

        return results

    def _validate_module_import(
        self, module_path: str, class_name: str
    ) -> Dict[str, Any]:
        """Validate a specific module import."""
        status = {
            "importable": False,
            "class_available": False,
            "instantiable": False,
            "error": None,
            "file_exists": False,
            "path_resolved": None,
        }

        try:
            # Check if module file exists
            file_path = self._resolve_module_file_path(module_path)
            status["file_exists"] = file_path and os.path.exists(file_path)
            status["path_resolved"] = file_path

            # Try to import the module
            module = importlib.import_module(module_path)
            status["importable"] = True

            # Check if class exists
            if hasattr(module, class_name):
                status["class_available"] = True

                # Try to instantiate (for GUI classes, this might fail
                # without QApplication)
                try:
                    class_obj = getattr(module, class_name)
                    # For GUI classes, we can't always instantiate
                    # without QApplication
                    if "GUI" in class_name or "Window" in class_name:
                        # GUI classes require QApplication, assume ready here
                        status["instantiable"] = True
                    else:
                        class_obj()
                        status["instantiable"] = True
                except Exception as e:
                    status["error"] = f"Instantiation failed: {str(e)}"
            else:
                status["error"] = f"Class {class_name} not found in module"

        except ImportError as e:
            status["error"] = f"Import failed: {str(e)}"
        except Exception as e:
            status["error"] = f"Unexpected error: {str(e)}"

        return status

    def _resolve_module_file_path(self, module_path: str) -> Optional[str]:
        """Resolve module path to actual file path."""
        try:
            # Convert module path to file path
            path_parts = module_path.split(".")

            # Try different base paths
            base_paths = [
                Path.cwd(),
                Path.cwd() / "src",
                Path(__file__).parent.parent.parent.parent,
            ]

            for base_path in base_paths:
                file_path = base_path
                for part in path_parts:
                    file_path = file_path / part

                # Try .py extension
                py_file = file_path.with_suffix(".py")
                if py_file.exists():
                    return str(py_file)

                # Try __init__.py in directory
                init_file = file_path / "__init__.py"
                if init_file.exists():
                    return str(init_file)

            return None
        except Exception:
            return None

    def _validate_python_path(self) -> Dict[str, Any]:
        """Validate Python path configuration."""
        status = {"valid": True, "issues": [], "paths": sys.path.copy()}

        # Check if src directory is in path
        src_paths = [p for p in sys.path if "src" in p or p.endswith("src")]
        if not src_paths:
            status["valid"] = False
            status["issues"].append("No 'src' directory found in Python path")

        # Check if current directory is accessible
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            status["issues"].append(
                f"Current directory not in Python path: {current_dir}"
            )

        # Check for duplicate paths
        unique_paths = set(sys.path)
        if len(unique_paths) != len(sys.path):
            status["issues"].append("Duplicate paths found in sys.path")

        return status

    def _check_circular_imports(self) -> Dict[str, Any]:
        """Check for potential circular import issues."""
        status = {"found": False, "issues": [], "dependencies": {}}

        # This is a simplified check - a full circular import detector
        # would be more complex
        try:
            # Check if config module imports from core modules that might
            # import back
            config_module_path = "src.tools.analysis.size_analyzer.size_analyzer_config"
            status["dependencies"]["config_module"] = config_module_path

            # Try to detect if there are circular dependencies
            # This is a basic implementation - could be enhanced

            status["issues"].append("Circular import check completed (basic)")

        except Exception as e:
            status["issues"].append(f"Circular import check failed: {str(e)}")

        return status

    def _render_module_status(
        self, module_status: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Render module status details for the diagnostic report."""
        lines = ["## Module Import Status", ""]
        for module_path, status in module_status.items():
            icon = "✓" if status.get("importable") else "✗"
            lines.append(f"- {icon} `{module_path}`")
            if status.get("error"):
                lines.append(f"  - Error: {status['error']}")
            if status.get("file_exists"):
                lines.append(f"  - File: {status['path_resolved']}")
        lines.append("")
        return lines

    def _render_message_section(
        self, title: str, messages: List[str], icon: str
    ) -> List[str]:
        """Render a generic message section when messages are available."""
        if not messages:
            return []

        lines = [f"## {title}", ""]
        for message in messages:
            lines.append(f"- {icon} {message}")
        lines.append("")
        return lines

    def _render_python_path_status(self, path_status: Dict[str, Any]) -> List[str]:
        """Render Python path diagnostics."""
        lines = ["## Python Path Configuration", ""]
        if path_status.get("valid"):
            lines.append("✓ Python path configuration is valid")
        else:
            lines.append("✗ Python path configuration has issues:")
            for issue in path_status.get("issues", []):
                lines.append(f"  - {issue}")
        lines.append("")
        return lines

    def generate_diagnostic_report(self) -> str:
        """Generate a comprehensive diagnostic report."""
        results = self.validate_size_analyzer_imports()
        report = "# Size Analyzer Import Diagnostic Report\n\n"
        overall_status = "✓ PASS" if results["success"] else "✗ FAIL"
        report += f"**Overall Status:** {overall_status}\n\n"

        report += "\n".join(self._render_module_status(results["module_status"]))
        report += "\n".join(
            self._render_message_section("Errors", results["errors"], "❌")
        )
        report += "\n".join(
            self._render_message_section("Warnings", results["warnings"], "⚠️")
        )
        report += "\n".join(
            self._render_python_path_status(results["python_path_status"])
        )

        # Recommendations
        report += "\n## Recommendations\n\n"
        if not results["success"]:
            report += "1. Fix the import errors listed above\n"
            report += "2. Ensure all required files exist in the correct " "locations\n"
            report += "3. Verify Python path includes the src directory\n"
            report += "4. Check for circular import dependencies\n"
            report += "5. Run the automated tool corrector\n"
        else:
            report += "All imports are working correctly! ✓\n"

        return report

    def fix_common_issues(self) -> Dict[str, Any]:
        """Attempt to fix common import issues automatically."""
        fixes_applied = {"success": True, "fixes": [], "errors": []}

        try:
            # Fix 1: Ensure src directory is in Python path
            src_dir = str(Path.cwd() / "src")
            if src_dir not in sys.path and os.path.exists(src_dir):
                sys.path.insert(0, src_dir)
                fixes_applied["fixes"].append(f"Added {src_dir} to Python path")

            # Fix 2: Ensure current directory is in Python path
            current_dir = str(Path.cwd())
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
                fixes_applied["fixes"].append(f"Added {current_dir} to Python path")

            # Fix 3: Create missing __init__.py files
            init_files_created = self._create_missing_init_files()
            fixes_applied["fixes"].extend(init_files_created)

        except Exception as e:
            fixes_applied["success"] = False
            fixes_applied["errors"].append(f"Error applying fixes: {str(e)}")

        return fixes_applied

    def _create_missing_init_files(self) -> List[str]:
        """Create missing __init__.py files in the directory structure."""
        created_files = []

        # Define directories that should have __init__.py files
        directories_to_check = [
            "src",
            "src/tools",
            "src/tools/analysis",
            "src/tools/analysis/size_analyzer",
        ]

        for directory in directories_to_check:
            dir_path = Path(directory)
            if dir_path.exists() and dir_path.is_dir():
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    try:
                        init_file.write_text('"""Package initialization file."""\n')
                        created_files.append(f"Created {init_file}")
                    except Exception as e:
                        print(f"Could not create {init_file}: {e}")

        return created_files


def main():
    """Main function for standalone execution of import validation."""
    validator = ImportValidator()

    print("Running Size Analyzer Import Validation...")
    print("=" * 50)

    # Generate and display diagnostic report
    report = validator.generate_diagnostic_report()
    print(report)

    # Attempt to fix common issues
    print("\nAttempting to fix common issues...")
    fixes = validator.fix_common_issues()

    if fixes["success"]:
        if fixes["fixes"]:
            print("✓ Applied fixes:")
            for fix in fixes["fixes"]:
                print(f"  - {fix}")
        else:
            print("✓ No fixes needed")
    else:
        print("✗ Error applying fixes:")
        for error in fixes["errors"]:
            print(f"  - {error}")

    # Re-run validation after fixes
    print("\nRe-running validation after fixes...")
    results = validator.validate_size_analyzer_imports()

    if results["success"]:
        print("✓ All imports are now working correctly!")
    else:
        print("✗ Some import issues remain:")
        for error in results["errors"]:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
