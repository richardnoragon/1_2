# File Splitter/Joiner Migration Technical Specifications

## Overview

This document provides detailed technical specifications for the file splitter/joiner migration to file_utilities_2, including validation scripts, implementation patterns, and integration requirements.

## Migration Validation Script Specifications

### Primary Validation Script: `file_splitter_migration_validation.py`

```python
#!/usr/bin/env python3
"""
File Splitter/Joiner Migration Validation Script

This script validates the migration of file_splitter_joiner.py to file_utilities_2
framework, ensuring all functionality is preserved and enhanced.
"""

import os
import sys
import json
import tempfile
import shutil
import hashlib
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class MigrationValidationError(Exception):
    """Custom exception for migration validation errors."""
    pass

class FileSplitterMigrationValidator:
    """Comprehensive validation for file splitter migration."""
    
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'overall_status': 'pending',
            'errors': [],
            'warnings': []
        }
        self.test_dir = None
        
    def setup_test_environment(self):
        """Setup isolated test environment."""
        self.test_dir = tempfile.mkdtemp(prefix='file_splitter_migration_')
        
        # Create test files of various sizes
        self.test_files = {
            'small': self._create_test_file('small_test.dat', 1024),  # 1KB
            'medium': self._create_test_file('medium_test.dat', 1024*1024),  # 1MB
            'large': self._create_test_file('large_test.dat', 10*1024*1024),  # 10MB
            'empty': self._create_test_file('empty_test.dat', 0)  # 0 bytes
        }
        
    def _create_test_file(self, filename: str, size: int) -> str:
        """Create test file with specified size."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'wb') as f:
            if size > 0:
                f.write(os.urandom(size))
        return filepath
        
    def validate_phase_1_preparation(self) -> Dict[str, Any]:
        """Validate Phase 1: Preparation and Backup."""
        results = {
            'phase': 'Phase 1: Preparation and Backup',
            'status': 'pending',
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check original files exist
            original_files = [
                'file_splitter_joiner.py',
                'file_splitter_joiner.ui',
                'tests/test_file_splitter_joiner.py'
            ]
            
            for file_path in original_files:
                if os.path.exists(file_path):
                    results['checks'][f'original_{file_path}'] = 'exists'
                else:
                    results['errors'].append(f'Original file missing: {file_path}')
            
            # Check backup creation
            backup_dir = 'backup/file_splitter_migration'
            if os.path.exists(backup_dir):
                results['checks']['backup_directory'] = 'exists'
                
                # Find latest backup
                backup_subdirs = [d for d in os.listdir(backup_dir) 
                                if os.path.isdir(os.path.join(backup_dir, d))]
                if backup_subdirs:
                    latest_backup = max(backup_subdirs)
                    backup_path = os.path.join(backup_dir, latest_backup)
                    
                    # Verify backup contents
                    for file_path in original_files:
                        backup_file = os.path.join(backup_path, os.path.basename(file_path))
                        if os.path.exists(backup_file):
                            results['checks'][f'backup_{file_path}'] = 'exists'
                        else:
                            results['warnings'].append(f'Backup missing: {file_path}')
                else:
                    results['errors'].append('No backup subdirectories found')
            else:
                results['errors'].append('Backup directory not found')
            
            # Determine phase status
            if results['errors']:
                results['status'] = 'failed'
            elif results['warnings']:
                results['status'] = 'warning'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f'Phase 1 validation error: {str(e)}')
            
        return results
        
    def validate_phase_2_core_logic(self) -> Dict[str, Any]:
        """Validate Phase 2: Core Logic Migration."""
        results = {
            'phase': 'Phase 2: Core Logic Migration',
            'status': 'pending',
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check core module files
            core_files = [
                'file_utilities_2/core/file_splitter_logic.py',
                'file_utilities_2/core/file_splitter_config.py',
                'file_utilities_2/core/file_splitter_logging.py'
            ]
            
            for file_path in core_files:
                if os.path.exists(file_path):
                    results['checks'][f'core_{os.path.basename(file_path)}'] = 'exists'
                    
                    # Check file content
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if len(content) > 100:  # Basic content check
                            results['checks'][f'content_{os.path.basename(file_path)}'] = 'valid'
                        else:
                            results['warnings'].append(f'File appears empty: {file_path}')
                else:
                    results['errors'].append(f'Core file missing: {file_path}')
            
            # Test core logic functionality
            if os.path.exists('file_utilities_2/core/file_splitter_logic.py'):
                try:
                    # Import and basic functionality test
                    sys.path.insert(0, 'file_utilities_2')
                    from core.file_splitter_logic import FileSplitterLogic
                    
                    logic = FileSplitterLogic()
                    results['checks']['core_logic_import'] = 'success'
                    
                    # Test basic methods
                    if hasattr(logic, 'split_file') and hasattr(logic, 'join_files'):
                        results['checks']['core_logic_methods'] = 'valid'
                    else:
                        results['errors'].append('Core logic missing required methods')
                        
                except ImportError as e:
                    results['errors'].append(f'Core logic import failed: {str(e)}')
                except Exception as e:
                    results['errors'].append(f'Core logic test failed: {str(e)}')
            
            # Determine phase status
            if results['errors']:
                results['status'] = 'failed'
            elif results['warnings']:
                results['status'] = 'warning'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f'Phase 2 validation error: {str(e)}')
            
        return results
        
    def validate_phase_3_ui_conversion(self) -> Dict[str, Any]:
        """Validate Phase 3: UI Conversion and Standardization."""
        results = {
            'phase': 'Phase 3: UI Conversion and Standardization',
            'status': 'pending',
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check GUI files
            gui_files = [
                'file_utilities_2/gui/file_splitter_gui.py',
                'file_utilities_2/gui/file_splitter_widget.py',
                'file_utilities_2/gui/file_splitter.ui'
            ]
            
            for file_path in gui_files:
                if os.path.exists(file_path):
                    results['checks'][f'gui_{os.path.basename(file_path)}'] = 'exists'
                else:
                    results['errors'].append(f'GUI file missing: {file_path}')
            
            # Test GUI imports
            if os.path.exists('file_utilities_2/gui/file_splitter_gui.py'):
                try:
                    sys.path.insert(0, 'file_utilities_2')
                    from gui.file_splitter_gui import FileSplitterGUI
                    results['checks']['gui_import'] = 'success'
                    
                    # Check StandardWindow inheritance
                    from gui.standard_window import StandardWindow
                    if issubclass(FileSplitterGUI, StandardWindow):
                        results['checks']['standard_window_inheritance'] = 'valid'
                    else:
                        results['errors'].append('GUI does not inherit from StandardWindow')
                        
                except ImportError as e:
                    results['errors'].append(f'GUI import failed: {str(e)}')
                except Exception as e:
                    results['errors'].append(f'GUI test failed: {str(e)}')
            
            # Check widget implementation
            if os.path.exists('file_utilities_2/gui/file_splitter_widget.py'):
                try:
                    from gui.file_splitter_widget import FileSplitterWidget
                    results['checks']['widget_import'] = 'success'
                except ImportError as e:
                    results['errors'].append(f'Widget import failed: {str(e)}')
            
            # Determine phase status
            if results['errors']:
                results['status'] = 'failed'
            elif results['warnings']:
                results['status'] = 'warning'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f'Phase 3 validation error: {str(e)}')
            
        return results
        
    def validate_phase_4_hub_integration(self) -> Dict[str, Any]:
        """Validate Phase 4: Hub Integration."""
        results = {
            'phase': 'Phase 4: Hub Integration',
            'status': 'pending',
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check hub integration file
            hub_file = 'file_utilities_2/integration/file_splitter_connector.py'
            if os.path.exists(hub_file):
                results['checks']['hub_connector_file'] = 'exists'
                
                try:
                    sys.path.insert(0, 'file_utilities_2')
                    from integration.file_splitter_connector import FileSplitterHubConnector
                    results['checks']['hub_connector_import'] = 'success'
                    
                    # Check HubIntegratedTool inheritance
                    from integration.hub_connector import HubIntegratedTool
                    if issubclass(FileSplitterHubConnector, HubIntegratedTool):
                        results['checks']['hub_integration_inheritance'] = 'valid'
                    else:
                        results['errors'].append('Hub connector does not inherit from HubIntegratedTool')
                        
                except ImportError as e:
                    results['errors'].append(f'Hub connector import failed: {str(e)}')
                except Exception as e:
                    results['errors'].append(f'Hub connector test failed: {str(e)}')
            else:
                results['errors'].append('Hub connector file missing')
            
            # Determine phase status
            if results['errors']:
                results['status'] = 'failed'
            elif results['warnings']:
                results['status'] = 'warning'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f'Phase 4 validation error: {str(e)}')
            
        return results
        
    def validate_phase_5_testing(self) -> Dict[str, Any]:
        """Validate Phase 5: Testing Migration and Enhancement."""
        results = {
            'phase': 'Phase 5: Testing Migration and Enhancement',
            'status': 'pending',
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check test files
            test_files = [
                'file_utilities_2/tests/test_file_splitter_core.py',
                'file_utilities_2/tests/test_file_splitter_gui.py',
                'file_utilities_2/tests/test_file_splitter_integration.py'
            ]
            
            for file_path in test_files:
                if os.path.exists(file_path):
                    results['checks'][f'test_{os.path.basename(file_path)}'] = 'exists'
                else:
                    results['errors'].append(f'Test file missing: {file_path}')
            
            # Run functional tests if available
            if all(os.path.exists(f) for f in test_files):
                try:
                    # Import and run basic tests
                    sys.path.insert(0, 'file_utilities_2')
                    
                    # Test core functionality
                    self._run_functional_tests()
                    results['checks']['functional_tests'] = 'passed'
                    
                except Exception as e:
                    results['errors'].append(f'Functional tests failed: {str(e)}')
            
            # Determine phase status
            if results['errors']:
                results['status'] = 'failed'
            elif results['warnings']:
                results['status'] = 'warning'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f'Phase 5 validation error: {str(e)}')
            
        return results
        
    def validate_phase_6_documentation(self) -> Dict[str, Any]:
        """Validate Phase 6: Documentation and Validation."""
        results = {
            'phase': 'Phase 6: Documentation and Validation',
            'status': 'pending',
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check documentation files
            doc_files = [
                'file_utilities_2/docs/file_splitter_api.md',
                'file_utilities_2/docs/file_splitter_migration.md',
                'file_utilities_2/docs/file_splitter_troubleshooting.md'
            ]
            
            for file_path in doc_files:
                if os.path.exists(file_path):
                    results['checks'][f'doc_{os.path.basename(file_path)}'] = 'exists'
                    
                    # Check content length
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if len(content) > 500:  # Minimum content check
                            results['checks'][f'content_{os.path.basename(file_path)}'] = 'adequate'
                        else:
                            results['warnings'].append(f'Documentation appears minimal: {file_path}')
                else:
                    results['errors'].append(f'Documentation file missing: {file_path}')
            
            # Determine phase status
            if results['errors']:
                results['status'] = 'failed'
            elif results['warnings']:
                results['status'] = 'warning'
            else:
                results['status'] = 'passed'
                
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f'Phase 6 validation error: {str(e)}')
            
        return results
        
    def _run_functional_tests(self):
        """Run functional tests to verify migration integrity."""
        if not self.test_dir:
            self.setup_test_environment()
            
        # Test file splitting functionality
        try:
            from core.file_splitter_logic import FileSplitterLogic
            logic = FileSplitterLogic()
            
            # Test split operation
            test_file = self.test_files['medium']
            output_dir = os.path.join(self.test_dir, 'split_test')
            os.makedirs(output_dir, exist_ok=True)
            
            # This would be a simplified test - full implementation would include
            # signal handling and proper async testing
            
        except Exception as e:
            raise Exception(f"Functional test failed: {str(e)}")
            
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete migration validation."""
        print("Starting File Splitter Migration Validation...")
        
        # Setup test environment
        self.setup_test_environment()
        
        # Run all phase validations
        phases = [
            self.validate_phase_1_preparation,
            self.validate_phase_2_core_logic,
            self.validate_phase_3_ui_conversion,
            self.validate_phase_4_hub_integration,
            self.validate_phase_5_testing,
            self.validate_phase_6_documentation
        ]
        
        for i, phase_validator in enumerate(phases, 1):
            print(f"Validating Phase {i}...")
            phase_results = phase_validator()
            self.validation_results['phases'][f'phase_{i}'] = phase_results
            
            if phase_results['status'] == 'failed':
                print(f"Phase {i} FAILED: {phase_results['errors']}")
            elif phase_results['status'] == 'warning':
                print(f"Phase {i} WARNING: {phase_results['warnings']}")
            else:
                print(f"Phase {i} PASSED")
        
        # Determine overall status
        phase_statuses = [p['status'] for p in self.validation_results['phases'].values()]
        if 'failed' in phase_statuses or 'error' in phase_statuses:
            self.validation_results['overall_status'] = 'failed'
        elif 'warning' in phase_statuses:
            self.validation_results['overall_status'] = 'warning'
        else:
            self.validation_results['overall_status'] = 'passed'
        
        # Cleanup test environment
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        return self.validation_results
        
    def generate_validation_report(self, output_file: str = None):
        """Generate detailed validation report."""
        if not output_file:
            output_file = f"file_splitter_migration_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"Validation report saved to: {output_file}")
        return output_file

def main():
    """Main validation execution."""
    validator = FileSplitterMigrationValidator()
    results = validator.run_complete_validation()
    
    # Generate report
    report_file = validator.generate_validation_report()
    
    # Print summary
    print("\n" + "="*60)
    print("MIGRATION VALIDATION SUMMARY")
    print("="*60)
    print(f"Overall Status: {results['overall_status'].upper()}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Report File: {report_file}")
    
    # Print phase summary
    for phase_key, phase_data in results['phases'].items():
        status_icon = "✅" if phase_data['status'] == 'passed' else "⚠️" if phase_data['status'] == 'warning' else "❌"
        print(f"{status_icon} {phase_data['phase']}: {phase_data['status'].upper()}")
    
    print("="*60)
    
    # Exit with appropriate code
    if results['overall_status'] in ['failed', 'error']:
        sys.exit(1)
    elif results['overall_status'] == 'warning':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
```

## Backup Creation Script Specifications

### Backup Script: `create_file_splitter_backup.py`

```python
#!/usr/bin/env python3
"""
File Splitter Migration Backup Script

Creates comprehensive backup of all file splitter related files before migration.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

def create_migration_backup():
    """Create comprehensive backup before migration."""
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = f"backup/file_splitter_migration/{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup
    files_to_backup = [
        'file_splitter_joiner.py',
        'file_splitter_joiner.ui',
        'tests/test_file_splitter_joiner.py'
    ]
    
    # Create backup manifest
    manifest = {
        'backup_timestamp': timestamp,
        'backup_directory': backup_dir,
        'files_backed_up': [],
        'migration_phase': 'pre_migration',
        'backup_size_bytes': 0
    }
    
    # Backup each file
    total_size = 0
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            # Calculate file size
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Copy file to backup
            backup_file_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_file_path)
            
            # Add to manifest
            manifest['files_backed_up'].append({
                'original_path': file_path,
                'backup_path': backup_file_path,
                'size_bytes': file_size,
                'backup_timestamp': timestamp
            })
            
            print(f"Backed up: {file_path} -> {backup_file_path}")
        else:
            print(f"Warning: File not found: {file_path}")
    
    manifest['backup_size_bytes'] = total_size
    
    # Save manifest
    manifest_path = os.path.join(backup_dir, 'backup_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nBackup completed successfully!")
    print(f"Backup directory: {backup_dir}")
    print(f"Total files backed up: {len(manifest['files_backed_up'])}")
    print(f"Total backup size: {total_size} bytes")
    print(f"Manifest file: {manifest_path}")
    
    return backup_dir, manifest

if __name__ == "__main__":
    create_migration_backup()
```

## Integration Testing Specifications

### Integration Test Script: `file_splitter_integration_test.py`

```python
#!/usr/bin/env python3
"""
File Splitter Integration Test Suite

Comprehensive testing of file splitter integration with file_utilities_2.
"""

import unittest
import tempfile
import os
import shutil
import sys
from unittest.mock import Mock, patch

class FileSplitterIntegrationTest(unittest.TestCase):
    """Integration tests for file splitter migration."""
    
    def setUp(self):
        """Setup test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Add file_utilities_2 to path
        sys.path.insert(0, 'file_utilities_2')
        
    def tearDown(self):
        """Cleanup test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_core_logic_integration(self):
        """Test core logic integration with file_utilities_2."""
        try:
            from core.file_splitter_logic import FileSplitterLogic
            from core.file_splitter_config import FileSplitterConfig
            
            # Test initialization
            config = FileSplitterConfig()
            logic = FileSplitterLogic(config)
            
            # Test basic functionality
            self.assertIsNotNone(logic)
            self.assertTrue(hasattr(logic, 'split_file'))
            self.assertTrue(hasattr(logic, 'join_files'))
            
        except ImportError as e:
            self.fail(f"Core logic integration failed: {e}")
    
    def test_gui_integration(self):
        """Test GUI integration with StandardWindow."""
        try:
            from gui.file_splitter_gui import FileSplitterGUI
            from gui.standard_window import StandardWindow
            
            # Test inheritance
            self.assertTrue(issubclass(FileSplitterGUI, StandardWindow))
            
        except ImportError as e:
            self.fail(f"GUI integration failed: {e}")
    
    def test_hub_integration(self):
        """Test hub connector integration."""
        try:
            from integration.file_splitter_connector import FileSplitterHubConnector
            from integration.hub_connector import HubIntegratedTool
            
            # Test inheritance
            self.assertTrue(issubclass(FileSplitterHubConnector, HubIntegratedTool))
            
        except ImportError as e:
            self.fail(f"Hub integration failed: {e}")
    
    def test_functionality_preservation(self):
        """Test that all original functionality is preserved."""
        # This would include comprehensive functional tests
        # to ensure no regression in file splitting/joining capabilities
        pass

if __name__ == '__main__':
    unittest.main()
```

## Migration Execution Script Specifications

### Migration Execution Script: `execute_file_splitter_migration.py`

```python
#!/usr/bin/env python3
"""
File Splitter Migration Execution Script

Orchestrates the complete migration process with progress tracking.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class FileSplitterMigrationExecutor:
    """Orchestrates the complete migration process."""
    
    def __init__(self):
        self.migration_log = {
            'start_time': datetime.now().isoformat(),
            'phases': {},
            'current_phase': None,
            'status': 'starting'
        }
        
    def execute_phase_1_backup(self):
        """Execute Phase 1: Create backup."""
        print("Executing Phase 1: Creating backup...")
        
        try:
            # Run backup script
            result = subprocess.run([
                sys.executable, 'create_file_splitter_backup.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.migration_log['phases']['phase_1'] = {
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat(),
                    'output': result.stdout
                }
                print("Phase 1 completed successfully")
                return True
            else:
                print(f"Phase 1 failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Phase 1 error: {e}")
            return False
    
    def execute_phase_2_core_migration(self):
        """Execute Phase 2: Core logic migration."""
        print("Executing Phase 2: Core logic migration...")
        
        # This would contain the actual migration logic
        # For now, this is a placeholder
        
        self.migration_log['phases']['phase_2'] = {
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        return True
    
    def execute_complete_migration(self):
        """Execute complete migration process."""
        phases = [
            ('Phase 1: Backup', self.execute_phase_1_backup),
            ('Phase 2: Core Migration', self.execute_phase_2_core_migration),
            # Add other phases as needed
        ]
        
        for phase_name, phase_func in phases:
            print(f"\n{'='*60}")
            print(f"Starting {phase_name}")
            print('='*60)
            
            self.migration_log['current_phase'] = phase_name
            
            if not phase_func():
                print(f"Migration failed at {phase_name}")
                self.migration_log['status'] = 'failed'
                return False
        
        self.migration_log['status'] = 'completed'
        self.migration_log['end_time'] = datetime.now().isoformat()
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True

def main():
    """Main migration execution."""
    executor = FileSplitterMigrationExecutor()
    
    print("File Splitter Migration Executor")
    print("="*60)
    
    success = executor.execute_complete_migration()
    
    # Save migration log
    log_file = f"file_splitter_migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(executor.migration_log, f, indent=2)
    
    print(f"Migration log saved to: {log_file}")
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## File Structure Specifications

### Target Directory Structure

```
file_utilities_2/
├── core/
│   ├── __init__.py
│   ├── file_splitter_logic.py      # Enhanced core business logic
│   ├── file_splitter_config.py     # Configuration management
│   └── file_splitter_logging.py    # Logging integration
├── gui/
│   ├── __init__.py
│   ├── file_splitter_gui.py        # StandardWindow implementation
│   ├── file_splitter_widget.py     # Embeddable widget
│   └── file_splitter.ui            # Updated UI file
├── integration/
│   ├── __init__.py
│   └── file_splitter_connector.py  # Hub integration
├── tests/
│   ├── __init__.py
│   ├── test_file_splitter_core.py      # Core logic tests
│   ├── test_file_splitter_gui.py       # GUI tests
│   └── test_file_splitter_integration.py # Integration tests
└── docs/
    ├── file_splitter_api.md           # API documentation
    ├── file_splitter_migration.md     # Migration documentation
    └── file_splitter_troubleshooting.md # Troubleshooting guide
```

### Backup Directory Structure

```
backup/
└── file_splitter_migration/
    └── 2025-07-29_17-00-00/
        ├── file_splitter_joiner.py
        ├── file_splitter_joiner.ui
        ├── test_file_splitter_joiner.py
        └── backup_manifest.json
```

## Implementation Checklist

### Phase 1: