#!/usr/bin/env python3
"""
Import Analysis Report for TagViewerEditor Migration
==================================================

This script analyzes the import statements and file structure to validate
the migration without requiring Python execution.
"""

import os
from pathlib import Path
from typing import Dict, List, Any

def analyze_file_structure() -> Dict[str, Any]:
    """Analyze the current file structure."""
    analysis = {
        'migrated_files': {},
        'legacy_files': {},
        'backup_files': {},
        'test_files': {},
        'integration_files': {}
    }
    
    # Check migrated files
    migrated_py = Path('file_utilities_2/gui/tag_viewer_editor.py')
    migrated_ui = Path('file_utilities_2/gui/tag_viewer_editor.ui')
    
    analysis['migrated_files']['tag_viewer_editor.py'] = {
        'exists': migrated_py.exists(),
        'path': str(migrated_py),
        'size': migrated_py.stat().st_size if migrated_py.exists() else 0
    }
    
    analysis['migrated_files']['tag_viewer_editor.ui'] = {
        'exists': migrated_ui.exists(),
        'path': str(migrated_ui),
        'size': migrated_ui.stat().st_size if migrated_ui.exists() else 0
    }
    
    # Check legacy files (should not exist)
    legacy_py = Path('tag_viewer_editor.py')
    legacy_ui = Path('tag_viewer_editor.ui')
    
    analysis['legacy_files']['tag_viewer_editor.py'] = {
        'exists': legacy_py.exists(),
        'path': str(legacy_py)
    }
    
    analysis['legacy_files']['tag_viewer_editor.ui'] = {
        'exists': legacy_ui.exists(),
        'path': str(legacy_ui)
    }
    
    # Check backup files
    backup_dir = Path('backup/tag_viewer_editor_migration')
    analysis['backup_files']['backup_directory'] = {
        'exists': backup_dir.exists(),
        'path': str(backup_dir)
    }
    
    if backup_dir.exists():
        for backup_subdir in backup_dir.iterdir():
            if backup_subdir.is_dir():
                analysis['backup_files'][backup_subdir.name] = {
                    'exists': True,
                    'path': str(backup_subdir),
                    'files': [f.name for f in backup_subdir.iterdir() if f.is_file()]
                }
    
    # Check test files
    test_files = [
        'tests/test_tag_viewer_editor.py',
        'tests/test_metadata.py'
    ]
    
    for test_file in test_files:
        test_path = Path(test_file)
        analysis['test_files'][test_path.name] = {
            'exists': test_path.exists(),
            'path': str(test_path)
        }
    
    # Check integration files
    integration_files = [
        'rfuhub.py',
        'file_utilities_2/gui/__init__.py'
    ]
    
    for int_file in integration_files:
        int_path = Path(int_file)
        analysis['integration_files'][int_path.name] = {
            'exists': int_path.exists(),
            'path': str(int_path)
        }
    
    return analysis

def analyze_import_statements() -> Dict[str, Any]:
    """Analyze import statements in relevant files."""
    import_analysis = {
        'migrated_file_imports': {},
        'test_file_imports': {},
        'integration_imports': {},
        'package_exports': {}
    }
    
    # Analyze migrated file imports
    migrated_file = Path('file_utilities_2/gui/tag_viewer_editor.py')
    if migrated_file.exists():
        try:
            with open(migrated_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            imports = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('from ') or line.startswith('import '):
                    imports.append(line)
            
            import_analysis['migrated_file_imports'] = {
                'file': str(migrated_file),
                'imports': imports,
                'count': len(imports)
            }
        except Exception as e:
            import_analysis['migrated_file_imports'] = {
                'error': str(e)
            }
    
    # Analyze test file imports
    test_files = [
        'tests/test_tag_viewer_editor.py',
        'tests/test_metadata.py'
    ]
    
    for test_file in test_files:
        test_path = Path(test_file)
        if test_path.exists():
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = []
                tag_viewer_imports = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('from ') or line.startswith('import '):
                        imports.append(line)
                        if 'tag_viewer_editor' in line.lower():
                            tag_viewer_imports.append(line)
                
                import_analysis['test_file_imports'][test_path.name] = {
                    'file': str(test_path),
                    'all_imports': imports,
                    'tag_viewer_imports': tag_viewer_imports,
                    'import_count': len(imports),
                    'tag_viewer_import_count': len(tag_viewer_imports)
                }
            except Exception as e:
                import_analysis['test_file_imports'][test_path.name] = {
                    'error': str(e)
                }
    
    # Analyze integration file imports
    rfuhub_file = Path('rfuhub.py')
    if rfuhub_file.exists():
        try:
            with open(rfuhub_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tag_viewer_imports = []
            for line in content.split('\n'):
                line = line.strip()
                if 'tag_viewer_editor' in line.lower() and ('import' in line or 'from' in line):
                    tag_viewer_imports.append(line)
            
            import_analysis['integration_imports']['rfuhub.py'] = {
                'file': str(rfuhub_file),
                'tag_viewer_imports': tag_viewer_imports,
                'count': len(tag_viewer_imports)
            }
        except Exception as e:
            import_analysis['integration_imports']['rfuhub.py'] = {
                'error': str(e)
            }
    
    # Analyze package exports
    init_file = Path('file_utilities_2/gui/__init__.py')
    if init_file.exists():
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            exports = []
            tag_viewer_exports = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('from ') and 'import' in line:
                    exports.append(line)
                    if 'tag_viewer_editor' in line.lower():
                        tag_viewer_exports.append(line)
                elif '__all__' in line:
                    exports.append(line)
            
            import_analysis['package_exports'] = {
                'file': str(init_file),
                'exports': exports,
                'tag_viewer_exports': tag_viewer_exports,
                'export_count': len(exports)
            }
        except Exception as e:
            import_analysis['package_exports'] = {
                'error': str(e)
            }
    
    return import_analysis

def validate_migration_integrity() -> Dict[str, Any]:
    """Validate the overall migration integrity."""
    validation = {
        'file_migration': {},
        'import_migration': {},
        'cleanup_status': {},
        'backup_integrity': {},
        'overall_status': 'UNKNOWN'
    }
    
    # File migration validation
    migrated_py_exists = Path('file_utilities_2/gui/tag_viewer_editor.py').exists()
    migrated_ui_exists = Path('file_utilities_2/gui/tag_viewer_editor.ui').exists()
    legacy_py_exists = Path('tag_viewer_editor.py').exists()
    legacy_ui_exists = Path('tag_viewer_editor.ui').exists()
    
    validation['file_migration'] = {
        'migrated_files_present': migrated_py_exists and migrated_ui_exists,
        'legacy_files_removed': not legacy_py_exists and not legacy_ui_exists,
        'status': 'PASSED' if (migrated_py_exists and migrated_ui_exists and not legacy_py_exists and not legacy_ui_exists) else 'FAILED'
    }
    
    # Import migration validation
    import_issues = []
    
    # Check test files for correct imports
    test_files = ['tests/test_tag_viewer_editor.py', 'tests/test_metadata.py']
    correct_imports = 0
    total_test_files = 0
    
    for test_file in test_files:
        test_path = Path(test_file)
        if test_path.exists():
            total_test_files += 1
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'from file_utilities_2.gui.tag_viewer_editor import TagViewerEditor' in content:
                    correct_imports += 1
                elif 'from tag_viewer_editor import TagViewerEditor' in content:
                    import_issues.append(f"{test_file}: Still using legacy import")
                else:
                    import_issues.append(f"{test_file}: No TagViewerEditor import found")
            except Exception as e:
                import_issues.append(f"{test_file}: Error reading file - {str(e)}")
    
    validation['import_migration'] = {
        'correct_imports': correct_imports,
        'total_test_files': total_test_files,
        'import_issues': import_issues,
        'status': 'PASSED' if correct_imports == total_test_files and len(import_issues) == 0 else 'FAILED'
    }
    
    # Cleanup status
    validation['cleanup_status'] = {
        'legacy_files_removed': not legacy_py_exists and not legacy_ui_exists,
        'status': 'PASSED' if not legacy_py_exists and not legacy_ui_exists else 'FAILED'
    }
    
    # Backup integrity
    backup_dir = Path('backup/tag_viewer_editor_migration')
    backup_exists = backup_dir.exists()
    backup_files_count = 0
    
    if backup_exists:
        for backup_subdir in backup_dir.iterdir():
            if backup_subdir.is_dir():
                backup_files_count += len([f for f in backup_subdir.iterdir() if f.is_file()])
    
    validation['backup_integrity'] = {
        'backup_directory_exists': backup_exists,
        'backup_files_count': backup_files_count,
        'status': 'PASSED' if backup_exists and backup_files_count > 0 else 'FAILED'
    }
    
    # Overall status
    all_passed = all(
        validation[key]['status'] == 'PASSED' 
        for key in ['file_migration', 'import_migration', 'cleanup_status', 'backup_integrity']
    )
    
    validation['overall_status'] = 'PASSED' if all_passed else 'FAILED'
    
    return validation

def generate_comprehensive_report() -> str:
    """Generate a comprehensive migration analysis report."""
    print("🔍 ANALYZING TAG_VIEWER_EDITOR MIGRATION STATUS")
    print("=" * 60)
    print()
    
    # Analyze file structure
    print("📁 FILE STRUCTURE ANALYSIS")
    print("-" * 30)
    file_analysis = analyze_file_structure()
    
    # Migrated files
    print("Migrated Files:")
    for filename, info in file_analysis['migrated_files'].items():
        status = "✅ EXISTS" if info['exists'] else "❌ MISSING"
        size = f"({info['size']} bytes)" if info['exists'] else ""
        print(f"  {filename}: {status} {size}")
    
    # Legacy files
    print("\nLegacy Files (should not exist):")
    for filename, info in file_analysis['legacy_files'].items():
        status = "❌ STILL EXISTS" if info['exists'] else "✅ REMOVED"
        print(f"  {filename}: {status}")
    
    # Backup files
    print("\nBackup Files:")
    backup_status = "✅ EXISTS" if file_analysis['backup_files']['backup_directory']['exists'] else "❌ MISSING"
    print(f"  Backup Directory: {backup_status}")
    
    print()
    
    # Analyze imports
    print("📦 IMPORT ANALYSIS")
    print("-" * 20)
    import_analysis = analyze_import_statements()
    
    # Test file imports
    print("Test File Imports:")
    for filename, info in import_analysis['test_file_imports'].items():
        if 'error' in info:
            print(f"  {filename}: ❌ ERROR - {info['error']}")
        else:
            print(f"  {filename}: {info['tag_viewer_import_count']} TagViewerEditor imports")
            for imp in info['tag_viewer_imports']:
                if 'file_utilities_2.gui.tag_viewer_editor' in imp:
                    print(f"    ✅ {imp}")
                else:
                    print(f"    ❌ {imp}")
    
    print()
    
    # Validation
    print("✅ MIGRATION VALIDATION")
    print("-" * 25)
    validation = validate_migration_integrity()
    
    for category, info in validation.items():
        if category == 'overall_status':
            continue
        
        status_icon = "✅" if info['status'] == 'PASSED' else "❌"
        print(f"{status_icon} {category.replace('_', ' ').title()}: {info['status']}")
        
        if 'import_issues' in info and info['import_issues']:
            for issue in info['import_issues']:
                print(f"    ⚠️ {issue}")
    
    print()
    print("🎯 OVERALL MIGRATION STATUS")
    print("-" * 30)
    overall_status = validation['overall_status']
    status_icon = "✅" if overall_status == 'PASSED' else "❌"
    print(f"{status_icon} Migration Status: {overall_status}")
    
    if overall_status == 'PASSED':
        print("\n🎉 MIGRATION SUCCESSFULLY COMPLETED!")
        print("All files migrated, imports updated, and cleanup completed.")
    else:
        print("\n⚠️ MIGRATION ISSUES DETECTED!")
        print("Review the analysis above for specific issues to address.")
    
    return overall_status

if __name__ == "__main__":
    status = generate_comprehensive_report()
    exit(0 if status == 'PASSED' else 1)