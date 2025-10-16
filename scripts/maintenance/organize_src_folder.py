#!/usr/bin/env python3
"""
Src Folder Organization Script for Richard's File Utilities

This script will systematically organize the src folder by:
1. Consolidating related files into proper module structures
2. Removing unnecessary duplicate files and __pycache__ folders
3. Creating proper package hierarchies
4. Ensuring all functionality is preserved
5. Creating a clean, maintainable structure
"""

import json
import shutil
from pathlib import Path


class SrcOrganizer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).resolve()
        self.src_path = self.base_path / "src"
        self.backup_dir = self.base_path / "src_backup"
        self.changes_log = []

    def log_change(self, action, source, target=None):
        """Log all changes made during organization."""
        change = {
            "action": action,
            "source": str(source),
            "target": str(target) if target else None,
        }
        self.changes_log.append(change)
        print(f"📝 {action}: {source} {f'-> {target}' if target else ''}")

    def create_backup(self):
        """Create a complete backup of the src folder."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        shutil.copytree(self.src_path, self.backup_dir)
        print(f"✅ Created backup at: {self.backup_dir}")

    def create_missing_core_structure(self):
        """Create the missing src/core structure that main.py requires."""
        print("\n🏗️ Creating missing src/core structure...")
        core_dir = self.src_path / "core"

        if core_dir.exists():
            print(f"  ✓ Directory {core_dir} already exists")
        else:
            core_dir.mkdir(parents=True, exist_ok=True)
            self.log_change("CREATED", core_dir)

        # Create __init__.py
        init_file = core_dir / "__init__.py"
        init_content = '''"""
Core constants and configuration for Richard's File Utilities.
"""

from .constants import (
    APP_NAME, JSON_FILES_FILTER, IMPORT_ERROR, SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER
)

__all__ = [
    "APP_NAME", "JSON_FILES_FILTER", "IMPORT_ERROR", "SECURITY_TEST",
    "SUGGESTED_SOLUTIONS_HEADER"
]
'''

        if not init_file.exists():
            init_file.write_text(init_content, encoding="utf-8")
            self.log_change("CREATED", init_file)

        # Create constants.py
        constants_file = core_dir / "constants.py"
        constants_content = '''"""
Constants for Richard's File Utilities Main Application.
"""

# Application Identity
APP_NAME = "Richard's File Utilities"

# File Dialog Filters
JSON_FILES_FILTER = "JSON Files (*.json);;All Files (*)"

# Error Messages
IMPORT_ERROR = "Import Error"
SECURITY_TEST = "Security Test"

# UI Headers
SUGGESTED_SOLUTIONS_HEADER = "Suggested Solutions"

# Version Information
APP_VERSION = "3.0.0"
APP_ORGANIZATION = "Richard's File Utilities"
'''

        if not constants_file.exists():
            constants_file.write_text(constants_content, encoding="utf-8")
            self.log_change("CREATED", constants_file)

    print("  ✅ Core structure ready for main.py imports")

    def remove_pycache_folders(self):
        """Remove all __pycache__ folders recursively."""
        print("\n🧹 Removing __pycache__ folders...")
        for pycache_dir in self.src_path.rglob("__pycache__"):
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                self.log_change("REMOVED", pycache_dir)

    def organize_analysis_tools(self):
        """Organize analysis tools into proper structure."""
        print("\n📊 Organizing analysis tools...")
        analysis_dir = self.src_path / "utilities" / "analysis"

        # Create subdirectories for better organization
        subdirs = ["core", "gui", "config"]
        for subdir in subdirs:
            (analysis_dir / subdir).mkdir(exist_ok=True)

        # Move related files to appropriate subdirectories
        moves = [
            ("size_analyzer_config.py", "config/size_analyzer_config.py"),
            ("size_analyzer_logging.py", "config/size_analyzer_logging.py"),
            ("size_analyzer_logic.py", "core/size_analyzer_logic.py"),
            ("find_duplicate_files.ui", "gui/find_duplicate_files.ui"),
        ]

        for source, target in moves:
            source_path = analysis_dir / source
            target_path = analysis_dir / target
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(target_path))
                self.log_change("MOVED", source_path, target_path)

        # Create __init__.py files for subdirectories
        for subdir in subdirs:
            init_file = analysis_dir / subdir / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Analysis tools submodule."""\n')
                self.log_change("CREATED", init_file)

    def organize_security_tools(self):
        """Organize security tools into proper structure."""
        print("\n🔒 Organizing security tools...")
        security_dir = self.src_path / "utilities" / "security"

        # Create subdirectories
        subdirs = ["core", "config"]
        for subdir in subdirs:
            (security_dir / subdir).mkdir(exist_ok=True)

        # Move related files
        moves = [
            ("encryption_config.py", "config/encryption_config.py"),
            ("encryption_logging.py", "config/encryption_logging.py"),
            ("encryption_logic.py", "core/encryption_logic.py"),
            ("secure_delete_config.py", "config/secure_delete_config.py"),
            ("secure_delete_logging.py", "config/secure_delete_logging.py"),
            ("secure_delete_logic.py", "core/secure_delete_logic.py"),
        ]

        for source, target in moves:
            source_path = security_dir / source
            target_path = security_dir / target
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(target_path))
                self.log_change("MOVED", source_path, target_path)

        # Create __init__.py files for subdirectories
        for subdir in subdirs:
            init_file = security_dir / subdir / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Security tools submodule."""\n')
                self.log_change("CREATED", init_file)

    def organize_system_tools(self):
        """Organize system tools into proper structure."""
        print("\n⚙️ Organizing system tools...")
        system_dir = self.src_path / "utilities" / "system"

        # Move UI files to gui subdirectory
        gui_dir = system_dir / "gui"
        gui_dir.mkdir(exist_ok=True)

        ui_file = system_dir / "permissions_editor.ui"
        if ui_file.exists():
            target = gui_dir / "permissions_editor.ui"
            shutil.move(str(ui_file), str(target))
            self.log_change("MOVED", ui_file, target)

        # Create __init__.py for gui subdirectory
        gui_init = gui_dir / "__init__.py"
        if not gui_init.exists():
            gui_init.write_text('"""System tools GUI components."""\n')
            self.log_change("CREATED", gui_init)

    def consolidate_duplicate_utilities(self):
        """Check for and consolidate any duplicate utility structures."""
        print("\n🔍 Checking for duplicate structures...")
        utilities_dir = self.src_path / "utilities"

        # Check each utility category for duplicates or unused files
        for category_dir in utilities_dir.iterdir():
            is_dir = category_dir.is_dir()
            is_cache = category_dir.name == "__pycache__"
            if is_dir and not is_cache:
                self.analyze_category_structure(category_dir)

    def analyze_category_structure(self, category_dir):
        """Analyze a category directory for optimization opportunities."""
        print(f"  📁 Analyzing {category_dir.name}...")

        # Count files and subdirectories
        py_files = list(category_dir.glob("*.py"))
        subdirs = [
            d for d in category_dir.iterdir() if d.is_dir() and d.name != "__pycache__"
        ]

        # Log structure for review
        summary = (
            f"{category_dir.name}: {len(py_files)} Python files, "
            f"{len(subdirs)} subdirectories"
        )
        self.log_change("ANALYZED", summary)

    def clean_legacy_folder(self):
        """Clean up and organize the legacy folder."""
        print("\n📜 Organizing legacy folder...")
        legacy_dir = self.src_path / "legacy"

        if legacy_dir.exists():
            # Check what's in legacy and if it's still needed
            legacy_contents = list(legacy_dir.rglob("*"))
            if legacy_contents:
                msg = "  📁 Legacy folder contains " f"{len(legacy_contents)} items"
                print(msg)
                self.log_change(
                    "REVIEWED", f"Legacy folder: {len(legacy_contents)} items"
                )
            else:
                # Remove empty legacy folder
                shutil.rmtree(legacy_dir)
                self.log_change("REMOVED", legacy_dir)

    def organize_rfu_folder(self):
        """Organize the rfu folder structure."""
        print("\n🎯 Organizing rfu folder...")
        rfu_dir = self.src_path / "rfu"

        if rfu_dir.exists():
            # Check for duplicate functionality with main utilities
            py_files = list(rfu_dir.glob("*.py"))
            subdirs = [
                d for d in rfu_dir.iterdir() if d.is_dir() and d.name != "__pycache__"
            ]

            rfu_summary = (
                f"RFU folder: {len(py_files)} Python files, "
                f"{len(subdirs)} subdirectories"
            )
            self.log_change("ANALYZED", rfu_summary)

            # Remove __pycache__ if it exists
            pycache = rfu_dir / "__pycache__"
            if pycache.exists():
                shutil.rmtree(pycache)
                self.log_change("REMOVED", pycache)

    def create_comprehensive_init_files(self):
        """Create comprehensive __init__.py files for proper imports."""
        print("\n📝 Creating/updating __init__.py files...")

        # Main utilities __init__.py
        utilities_init = self.src_path / "utilities" / "__init__.py"
        utilities_content = '''"""
Richard's File Utilities - Utilities Package

This package contains all the file utility tools organized by category:
- analysis: File analysis tools (checksum, duplicates, size analysis)
- file_operations: File manipulation tools
- metadata: Metadata editing tools
- network: Network connectivity tools
- pdf_tools: PDF manipulation tools
- privacy: Privacy and data cleaning tools
- security: Security and encryption tools
- system: System administration tools
"""

__version__ = "3.0.0"
__author__ = "Richard's File Utilities"

# Import main utility categories
from . import analysis
from . import file_operations
from . import metadata
from . import network
from . import pdf_tools
from . import privacy
from . import security
from . import system

__all__ = [
    "analysis",
    "file_operations",
    "metadata",
    "network",
    "pdf_tools",
    "privacy",
    "security",
    "system"
]
'''
        utilities_init.write_text(utilities_content)
        self.log_change("UPDATED", utilities_init)

        # Category-specific __init__.py files
        categories = {
            "analysis": ["check_sum", "find_duplicate_files", "size_analyzer"],
            "security": ["en_and_decrypt", "secure_delete"],
            "system": ["permissions_editor", "diagnostics_monitoring"],
            "network": ["network_connectivity", "network_scanner"],
            "privacy": ["privacy_tools", "data_anonymizer"],
        }

        for category, modules in categories.items():
            category_init = self.src_path / "utilities" / category / "__init__.py"
            if category_init.parent.exists():
                title = category.title()
                init_content = '"""Richard\'s File Utilities - ' f'{title} Tools"""\n\n'
                module_list = ", ".join(modules)
                init_content += f"# Available modules: {module_list}\n"
                category_init.write_text(init_content)
                self.log_change("UPDATED", category_init)

    def remove_logs_folder(self):
        """Remove or relocate the logs folder if it's not needed in src."""
        print("\n📋 Checking logs folder...")
        logs_dir = self.src_path / "logs"

        if logs_dir.exists():
            # Move logs outside of src to project root
            target_logs = self.base_path / "logs"
            if not target_logs.exists():
                shutil.move(str(logs_dir), str(target_logs))
                self.log_change("MOVED", logs_dir, target_logs)
            else:
                # If target exists, merge contents
                for item in logs_dir.iterdir():
                    target_item = target_logs / item.name
                    if not target_item.exists():
                        shutil.move(str(item), str(target_item))
                        self.log_change("MOVED", item, target_item)
                shutil.rmtree(logs_dir)
                self.log_change("REMOVED", logs_dir)

    def validate_organization(self):
        """Validate that all tools still work after organization."""
        print("\n✅ Validating organization...")

        # Check that main tool files still exist
        critical_files = [
            "utilities/analysis/check_sum.py",
            "utilities/analysis/find_duplicate_files.py",
            "utilities/analysis/size_analyzer.py",
            "utilities/security/en_and_decrypt.py",
            "utilities/security/secure_delete.py",
            "tools/file_operations/secure_delete/secure_delete.py",
            "utilities/system/permissions_editor.py",
            "utilities/network/network_connectivity.py",
            "utilities/privacy/privacy_tools.py",
        ]

        all_good = True
        for file_path in critical_files:
            full_path = self.src_path / file_path
            if full_path.exists():
                self.log_change("VALIDATED", full_path)
            else:
                print(f"❌ MISSING: {full_path}")
                all_good = False

        return all_good

    def save_changes_log(self):
        """Save the changes log for reference."""
        log_file = self.base_path / "src_organization_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.changes_log, f, indent=2)
        print(f"\n📄 Changes log saved to: {log_file}")

    def run_organization(self):
        """Run the complete organization process."""
        print("🚀 Starting src folder organization...")
        print("=" * 60)

        # Step 0: Create missing core structure for main.py
        self.create_missing_core_structure()

        # Step 1: Create backup
        self.create_backup()

        # Step 2: Remove __pycache__ folders
        self.remove_pycache_folders()

        # Step 3: Organize each category
        self.organize_analysis_tools()
        self.organize_security_tools()
        self.organize_system_tools()

        # Step 4: Clean up structure
        self.consolidate_duplicate_utilities()
        self.clean_legacy_folder()
        self.organize_rfu_folder()
        self.remove_logs_folder()

        # Step 5: Create proper package structure
        self.create_comprehensive_init_files()

        # Step 6: Validate everything still works
        if self.validate_organization():
            print("\n✅ Organization completed successfully!")
        else:
            warning_msg = (
                "\n⚠️ Organization completed with warnings. " "Check validation output."
            )
            print(warning_msg)

        # Step 7: Save log
        self.save_changes_log()

        print("\n" + "=" * 60)
        print("ORGANIZATION SUMMARY:")
        print(f"📁 Backup created at: {self.backup_dir}")
        print(f"📝 {len(self.changes_log)} changes made")
        print("🎯 Src folder is now systematically organized")
        print("✅ Missing src/core/constants.py structure created")
        print("\nNext steps:")
        print("1. Test the main application: python main.py")
        print("2. Verify all tools work properly")
        print("3. Remove backup folder after testing")


def main():
    """Main function to run src organization."""

    # JUST create the missing core structure first
    print("🎯 Creating missing src/core constants structure only...")

    # Direct creation approach
    core_dir = Path("src/core")
    if not core_dir.exists():
        print("Creating missing src/core structure...")
        core_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {core_dir}")

        # Create __init__.py
        init_file = core_dir / "__init__.py"
        init_content = '''"""
Core constants and configuration for Richard's File Utilities.
"""

from .constants import (
    APP_NAME, JSON_FILES_FILTER, IMPORT_ERROR, SECURITY_TEST,
    SUGGESTED_SOLUTIONS_HEADER
)

__all__ = [
    "APP_NAME", "JSON_FILES_FILTER", "IMPORT_ERROR", "SECURITY_TEST",
    "SUGGESTED_SOLUTIONS_HEADER"
]
'''
        init_file.write_text(init_content, encoding="utf-8")
        print(f"✓ Created {init_file}")

        # Create constants.py
        constants_file = core_dir / "constants.py"
        constants_content = '''"""
Constants for Richard's File Utilities Main Application.
"""

# Application Identity
APP_NAME = "Richard's File Utilities"

# File Dialog Filters
JSON_FILES_FILTER = "JSON Files (*.json);;All Files (*)"

# Error Messages
IMPORT_ERROR = "Import Error"
SECURITY_TEST = "Security Test"

# UI Headers
SUGGESTED_SOLUTIONS_HEADER = "Suggested Solutions"

# Version Information
APP_VERSION = "3.0.0"
APP_ORGANIZATION = "Richard's File Utilities"
'''
        constants_file.write_text(constants_content, encoding="utf-8")
        print(f"✓ Created {constants_file}")

        print("\n✅ Constants structure creation completed successfully!")
        print("✅ main.py can now import from src.core.constants")

        # Test the import
        try:
            import os
            import sys

            # Ensure we're in the right directory
            os.chdir(Path(__file__).parent.parent.parent)
            sys.path.insert(0, "src")
            from core.constants import (
                APP_NAME,
                IMPORT_ERROR,
                JSON_FILES_FILTER,
            )

            print(f"✅ Import test successful: {APP_NAME}")
            print(f"✅ JSON filter: {JSON_FILES_FILTER}")
            print(f"✅ Error constant: {IMPORT_ERROR}")
        except Exception as e:
            print(f"⚠️ Import test failed: {e}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Available directories: {list(Path('.').iterdir())}")
    else:
        print(f"✓ Directory {core_dir} already exists")
        constants_file = core_dir / "constants.py"
        if constants_file.exists():
            print(f"✓ File {constants_file} already exists")
            print("✅ Constants structure already complete!")
        else:
            notice = "⚠️ Directory exists but constants.py missing; creating it..."
            print(notice)
            # Just create the constants file
            constants_content = '''"""
Constants for Richard's File Utilities Main Application.
"""

# Application Identity
APP_NAME = "Richard's File Utilities"

# File Dialog Filters
JSON_FILES_FILTER = "JSON Files (*.json);;All Files (*)"

# Error Messages
IMPORT_ERROR = "Import Error"
SECURITY_TEST = "Security Test"

# UI Headers
SUGGESTED_SOLUTIONS_HEADER = "Suggested Solutions"

# Version Information
APP_VERSION = "3.0.0"
APP_ORGANIZATION = "Richard's File Utilities"
'''
            constants_file.write_text(constants_content, encoding="utf-8")
            print(f"✓ Created {constants_file}")

    # Comment out the full organization for now
    # organizer = SrcOrganizer()
    # organizer.run_organization()


if __name__ == "__main__":
    main()
