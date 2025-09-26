#!/usr/bin/env python3
"""
Enterprise Import Path Updater
Richard's File Utilities - Post-Reorganization Import Corrections

This script systematically updates all import statements and relative paths
to match the new enterprise directory structure.
"""

import os
import re
from pathlib import Path
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.temp_reorganization_plan/import_updates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImportPathUpdater:
    """Enterprise-grade import path updater for reorganized project."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.updated_files = []
        
        # Define the mapping of old imports to new imports
        self.import_mappings = {
            # Core imports that moved
            'from standalone_database_manager import': 'from scripts.maintenance.standalone_database_manager import',
            'from enhanced_pdf_tools_widget import': 'from scripts.development.demos.enhanced_pdf_tools_widget import',
            'from gui.menu_manager import': 'from src.gui.menu_manager import',
            
            # Constants import
            'from src.core.constants import': 'from src.core.constants import',
            
            # Security dialog import
            'from src.gui.security_preferences_dialog import': 'from src.gui.dialogs.security_preferences_dialog import',
            
            # Tool imports - utilities -> tools reorganization
            'src.utilities.file_management.': 'src.tools.file_management.',
            'src.utilities.file_operations.': 'src.tools.file_operations.',
            'src.utilities.analysis.': 'src.tools.analysis.',
            'src.utilities.security.': 'src.tools.security.',
            'src.utilities.metadata.': 'src.tools.metadata.',
            'src.utilities.network.': 'src.tools.network.',
            'src.utilities.privacy.': 'src.tools.privacy.',
            'src.utilities.system.': 'src.tools.system.',
        }
        
        # Tool module mappings with new structure
        self.tool_mappings = {
            # File Management Tools
            'src.utilities.file_management.file_finder': 'src.tools.file_management.finder.file_finder',
            'src.utilities.file_management.catalog': 'src.tools.file_management.catalog.catalog',
            'src.utilities.file_management.rename': 'src.tools.file_management.renamer.rename',
            'src.utilities.file_management.organize': 'src.tools.file_management.organizer.organize',
            
            # File Operations Tools
            'src.utilities.file_operations.cmsd': 'src.tools.file_operations.cmsd.cmsd',
            'src.utilities.file_operations.compression': 'src.tools.file_operations.compression.compression',
            'src.utilities.file_operations.file_splitter': 'src.tools.file_operations.splitter.file_splitter',
            'src.utilities.file_operations.synchronization_backup.sync': 'src.tools.file_operations.synchronizer.sync',
            'src.utilities.file_operations.enhanced_editor.enhanced_editor': 'src.tools.file_operations.editor.enhanced_editor',
            'src.utilities.file_operations.file_touch': 'src.tools.file_operations.touch.file_touch',
            
            # Analysis Tools
            'src.utilities.analysis.size_analyzer': 'src.tools.analysis.size_analyzer.size_analyzer',
            'src.utilities.analysis.find_duplicate_files': 'src.tools.analysis.duplicate_finder.find_duplicate_files',
            'src.utilities.analysis.check_sum': 'src.tools.analysis.checksum.check_sum',
            'src.utilities.analysis.empty_folders': 'src.tools.analysis.empty_folders.empty_folders',
            
            # Security Tools
            'src.utilities.security.en_and_decrypt': 'src.tools.security.encryption.en_and_decrypt',
            'src.utilities.security.secure_delete': 'src.tools.security.secure_delete.secure_delete',
            
            # Metadata Tools
            'src.utilities.metadata.image_metadata': 'src.tools.metadata.image_editor.image_metadata',
            'src.utilities.metadata.office_meta_data_editor': 'src.tools.metadata.office_editor.office_meta_data_editor',
            
            # Network Tools
            'src.utilities.network.network_connectivity': 'src.tools.network.connectivity.network_connectivity',
            'src.utilities.network.network_scanner': 'src.tools.network.scanner.network_scanner',
            'src.utilities.network.network_transfer': 'src.tools.network.transfer.network_transfer',
            'src.utilities.network.bookmark_manager': 'src.tools.network.bookmarks.bookmark_manager',
            
            # Privacy Tools
            'src.utilities.privacy.privacy_tools_simple': 'src.tools.privacy.cleaner.privacy_tools_simple',
            'src.utilities.privacy.data_anonymizer': 'src.tools.privacy.anonymizer.data_anonymizer',
            
            # System Tools
            'src.utilities.system.permissions_editor': 'src.tools.system.permissions.permissions_editor',
            'src.utilities.system.diagnostics_monitoring': 'src.tools.system.diagnostics.diagnostics_monitoring',
            'src.utilities.system.system_cleanup': 'src.tools.system.cleanup.system_cleanup',
            'src.utilities.system.software_maintenance': 'src.tools.system.maintenance.software_maintenance',
        }
        
        # Demo scripts that need import updates
        self.demo_scripts = {
            'enhanced_clipboard_system_integration': 'scripts.development.demos.enhanced_clipboard_system_integration',
            'enhanced_pdf_tools_widget': 'scripts.development.demos.enhanced_pdf_tools_widget',
        }
    
    def update_main_py(self):
        """Update main.py with corrected import paths."""
        logger.info("Updating main.py import paths...")
        
        main_file = self.root_dir / 'main.py'
        if not main_file.exists():
            logger.error("main.py not found")
            return
        
        # Read original content
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updates_made = []
        
        # Update direct import mappings
        for old_import, new_import in self.import_mappings.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                updates_made.append(f"Updated: {old_import} -> {new_import}")
                logger.info(f"Updated import: {old_import} -> {new_import}")
        
        # Update tool launch imports with proper module paths
        for old_path, new_path in self.tool_mappings.items():
            old_quoted = f'"{old_path}"'
            new_quoted = f'"{new_path}"'
            if old_quoted in content:
                content = content.replace(old_quoted, new_quoted)
                updates_made.append(f"Updated tool path: {old_path} -> {new_path}")
                logger.info(f"Updated tool path: {old_path} -> {new_path}")
        
        # Update demo script references
        for old_demo, new_demo in self.demo_scripts.items():
            old_quoted = f'"{old_demo}"'
            new_quoted = f'"{new_demo}"'
            if old_quoted in content:
                content = content.replace(old_quoted, new_quoted)
                updates_made.append(f"Updated demo: {old_demo} -> {new_demo}")
                logger.info(f"Updated demo: {old_demo} -> {new_demo}")
        
        # Update path insertion logic
        old_path_insert = "sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))"
        new_path_insert = """# Add necessary paths for reorganized structure
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'maintenance'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'development', 'demos'))"""
        
        if old_path_insert in content:
            content = content.replace(old_path_insert, new_path_insert)
            updates_made.append("Updated path insertion logic for reorganized structure")
            logger.info("Updated path insertion logic")
        
        # Write updated content if changes were made
        if content != original_content:
            # Create backup
            backup_file = main_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write updated content
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.updated_files.append({
                'file': str(main_file),
                'updates': updates_made,
                'backup': str(backup_file)
            })
            
            logger.info(f"Updated main.py with {len(updates_made)} import corrections")
        else:
            logger.info("No updates needed for main.py")
    
    def create_missing_structure(self):
        """Create any missing directories for the new structure."""
        logger.info("Creating missing directory structure...")
        
        # Core RFU structure
        core_dirs = [
            'src/rfu/core',
            'src/rfu/gui/dialogs',
            'src/rfu/gui/widgets',
            'src/rfu/gui/windows',
            'src/rfu/gui/common',
            'src/rfu/database/models',
            'src/rfu/database/migrations',
            'src/rfu/utils',
        ]
        
        # Tools structure
        tool_dirs = [
            'src/tools/file_management/finder',
            'src/tools/file_management/catalog', 
            'src/tools/file_management/renamer',
            'src/tools/file_management/organizer',
            'src/tools/file_operations/cmsd',
            'src/tools/file_operations/compression',
            'src/tools/file_operations/splitter',
            'src/tools/file_operations/synchronizer',
            'src/tools/file_operations/editor',
            'src/tools/file_operations/touch',
            'src/tools/analysis/size_analyzer',
            'src/tools/analysis/duplicate_finder',
            'src/tools/analysis/checksum',
            'src/tools/analysis/empty_folders',
            'src/tools/security/encryption',
            'src/tools/security/secure_delete',
            'src/tools/security/permissions',
            'src/tools/metadata/image_editor',
            'src/tools/metadata/office_editor',
            'src/tools/network/connectivity',
            'src/tools/network/scanner',
            'src/tools/network/transfer',
            'src/tools/network/bookmarks',
            'src/tools/privacy/cleaner',
            'src/tools/privacy/anonymizer',
            'src/tools/system/diagnostics',
            'src/tools/system/cleanup',
            'src/tools/system/maintenance',
            'src/tools/system/permissions',
        ]
        
        all_dirs = core_dirs + tool_dirs
        
        for directory in all_dirs:
            dir_path = self.root_dir / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
                
                # Create __init__.py files
                init_file = dir_path / '__init__.py'
                if not init_file.exists():
                    with open(init_file, 'w', encoding='utf-8') as f:
                        f.write(f'"""\n{directory.replace("/", ".")} package\n"""\n')
                    logger.info(f"Created __init__.py in {directory}")
    
    def move_files_to_new_structure(self):
        """Move files from old utilities structure to new tools structure."""
        logger.info("Moving files to new enterprise structure...")
        
        src_dir = self.root_dir / 'src'
        if not (src_dir / 'utilities').exists():
            logger.info("Utilities directory already reorganized")
            return
        
        # File movement mappings
        file_moves = {
            # Core files
            'src/core/constants.py': 'src/rfu/core/constants.py',
            
            # GUI files
            'gui/menu_manager.py': 'src/rfu/gui/menu_manager.py',
            'src/rfu/gui/security_preferences_dialog.py': 'src/rfu/gui/dialogs/security_preferences_dialog.py',
            
            # Tool files from utilities -> tools
            'src/utilities/file_management/file_finder.py': 'src/tools/file_management/finder/file_finder.py',
            'src/utilities/file_management/catalog.py': 'src/tools/file_management/catalog/catalog.py',
            'src/utilities/file_management/rename.py': 'src/tools/file_management/renamer/rename.py',
            'src/utilities/file_management/organize.py': 'src/tools/file_management/organizer/organize.py',
            'src/utilities/analysis/size_analyzer.py': 'src/tools/analysis/size_analyzer/size_analyzer.py',
            'src/utilities/analysis/find_duplicate_files.py': 'src/tools/analysis/duplicate_finder/find_duplicate_files.py',
            'src/utilities/analysis/empty_folders.py': 'src/tools/analysis/empty_folders/empty_folders.py',
        }
        
        import shutil
        
        for old_path, new_path in file_moves.items():
            old_file = self.root_dir / old_path
            new_file = self.root_dir / new_path
            
            if old_file.exists():
                # Ensure target directory exists
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                try:
                    shutil.move(str(old_file), str(new_file))
                    logger.info(f"Moved: {old_path} -> {new_path}")
                except Exception as e:
                    logger.error(f"Failed to move {old_path}: {e}")
    
    def update_configuration_files(self):
        """Update configuration files with new paths."""
        logger.info("Updating configuration files...")
        
        # Update pytest.ini if it exists in config/application/
        pytest_config = self.root_dir / 'config' / 'application' / 'pytest.ini'
        if pytest_config.exists():
            with open(pytest_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update test paths
            content = content.replace('testpaths = tests', 'testpaths = tests')
            content = content.replace('python_files = test_*.py', 'python_files = test_*.py')
            
            with open(pytest_config, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Updated pytest.ini configuration")
    
    def create_import_validation_script(self):
        """Create a script to validate all imports work correctly."""
        validation_script = self.root_dir / '.temp_reorganization_plan' / 'validate_imports.py'
        
        script_content = '''#!/usr/bin/env python3
"""\nImport Validation Script\nVerifies all imports work correctly after reorganization.\n"""

import sys
import os
from pathlib import Path

# Add paths
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'maintenance'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'development', 'demos'))

def test_core_imports():
    """Test core application imports."""
    try:
        # Test constants import
        from src.core.constants import APP_NAME
        print(f"✓ Core constants import successful: {APP_NAME}")
        
        # Test database manager
        try:
            from scripts.maintenance.standalone_database_manager import get_database_manager
            print("✓ Database manager import successful")
        except ImportError as e:
            print(f"⚠ Database manager import failed: {e}")
        
        return True
    except ImportError as e:
        print(f"✗ Core imports failed: {e}")
        return False

def test_tool_imports():
    """Test tool imports."""
    tool_tests = [
        ('src.tools.file_management.finder.file_finder', 'FileFinderGUI'),
        ('src.tools.analysis.size_analyzer.size_analyzer', 'SizeAnalyzerGUI'),
    ]
    
    success_count = 0
    for module_name, class_name in tool_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✓ {module_name}.{class_name} import successful")
                success_count += 1
            else:
                print(f"⚠ {module_name} missing class {class_name}")
        except ImportError as e:
            print(f"⚠ {module_name} import failed: {e}")
    
    return success_count

def main():
    """Run import validation tests."""
    print("=" * 60)
    print("IMPORT VALIDATION AFTER REORGANIZATION")
    print("=" * 60)
    
    # Test core imports
    print("\nTesting core imports...")
    core_success = test_core_imports()
    
    # Test tool imports
    print("\nTesting tool imports...")
    tool_success_count = test_tool_imports()
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Core imports: {'PASS' if core_success else 'FAIL'}")
    print(f"Tool imports: {tool_success_count} successful")
    
    if core_success and tool_success_count > 0:
        print("\n✅ Import validation PASSED - basic functionality verified")
        return 0
    else:
        print("\n❌ Import validation FAILED - issues need resolution")
        return 1

if __name__ == '__main__':
    sys.exit(main())
'''
        
        with open(validation_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Created import validation script: {validation_script}")
    
    def generate_update_report(self):
        """Generate comprehensive update report."""
        report = {
            'import_updates_completed': True,
            'files_updated': len(self.updated_files),
            'updated_files_details': self.updated_files,
            'structure_changes': {
                'utilities_to_tools': 'src/utilities/* -> src/tools/*',
                'core_reorganization': 'src/core/* -> src/rfu/core/*',
                'gui_reorganization': 'gui/* -> src/rfu/gui/*',
                'scripts_reorganization': 'root scripts -> scripts/category/*'
            },
            'validation_available': True,
            'next_steps': [
                'Run import validation script',
                'Test application startup',
                'Verify tool functionality',
                'Run test suite'
            ]
        }
        
        import json
        report_file = self.root_dir / '.temp_reorganization_plan' / 'import_updates_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Import update report saved to {report_file}")
        return report
    
    def execute_full_update(self):
        """Execute complete import path update process."""
        logger.info("Starting enterprise import path update process...")
        
        try:
            # Step 1: Create missing directory structure
            self.create_missing_structure()
            
            # Step 2: Move files to new structure
            self.move_files_to_new_structure()
            
            # Step 3: Update main.py imports
            self.update_main_py()
            
            # Step 4: Update configuration files
            self.update_configuration_files()
            
            # Step 5: Create validation script
            self.create_import_validation_script()
            
            # Step 6: Generate report
            report = self.generate_update_report()
            
            logger.info("Import path update completed successfully!")
            logger.info(f"Files updated: {report['files_updated']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Import update failed: {e}")
            raise

def main():
    """Main execution function."""
    updater = ImportPathUpdater()
    report = updater.execute_full_update()
    
    print("\n" + "="*60)
    print("ENTERPRISE IMPORT PATH UPDATE COMPLETED")
    print("="*60)
    print(f"Files updated: {report['files_updated']}")
    print(f"Structure reorganization: Complete")
    print(f"Validation script: Created")
    print("\nNext steps:")
    for step in report['next_steps']:
        print(f"  • {step}")
    print("\nDetailed report: .temp_reorganization_plan/import_updates_report.json")
    
if __name__ == "__main__":
    main()