#!/usr/bin/env python3
"""Enterprise QA Validation - Post-Reorganization Quality Assurance"""

import os
import json
from pathlib import Path
from datetime import datetime

class EnterpriseQAValidator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.results = {'timestamp': datetime.now().isoformat()}
    
    def validate_root_directory(self):
        """Validate root directory compliance (≤10 files)."""
        root_files = [f for f in self.root_dir.iterdir() if f.is_file()]
        file_count = len(root_files)
        
        status = 'PASS' if file_count <= 10 else 'FAIL'
        return {
            'status': status,
            'file_count': file_count,
            'max_allowed': 10,
            'files': [f.name for f in root_files]
        }
    
    def validate_directory_structure(self):
        """Validate enterprise directory structure."""
        required_dirs = ['docs', 'scripts', 'src', 'tests', 'config', 'assets']
        enterprise_dirs = ['docs/api', 'docs/architecture', 'scripts/maintenance', 'src/rfu/core', 'src/tools']
        
        missing_required = [d for d in required_dirs if not (self.root_dir / d).exists()]
        missing_enterprise = [d for d in enterprise_dirs if not (self.root_dir / d).exists()]
        
        status = 'PASS' if len(missing_required) == 0 else 'FAIL'
        return {
            'status': status,
            'missing_required': missing_required,
            'missing_enterprise': missing_enterprise
        }
    
    def validate_imports(self):
        """Validate critical imports work."""
        import sys
        sys.path.insert(0, str(self.root_dir))
        sys.path.insert(0, str(self.root_dir / 'src'))
        
        import_tests = {}
        
        # Test core constants
        try:
            from src.rfu.core.constants import APP_NAME
            import_tests['core_constants'] = {'status': 'PASS', 'value': APP_NAME}
        except ImportError as e:
            import_tests['core_constants'] = {'status': 'FAIL', 'error': str(e)}
        
        # Test database manager
        try:
            from scripts.maintenance.standalone_database_manager import get_database_manager
            import_tests['database_manager'] = {'status': 'PASS'}
        except ImportError as e:
            import_tests['database_manager'] = {'status': 'FAIL', 'error': str(e)}
        
        # Test GUI components
        try:
            from src.rfu.gui.menu_manager import MenuManager
            import_tests['menu_manager'] = {'status': 'PASS'}
        except ImportError as e:
            import_tests['menu_manager'] = {'status': 'FAIL', 'error': str(e)}
        
        passed = sum(1 for t in import_tests.values() if t['status'] == 'PASS')
        return {
            'status': 'PASS' if passed >= 2 else 'FAIL',
            'tests': import_tests,
            'passed': passed,
            'total': len(import_tests)
        }
    
    def run_full_validation(self):
        """Run complete QA validation."""
        print("ENTERPRISE QA VALIDATION")
        print("=" * 50)
        
        # Root directory validation
        root_result = self.validate_root_directory()
        print(f"Root Directory: {root_result['status']} ({root_result['file_count']}/10 files)")
        
        # Structure validation
        struct_result = self.validate_directory_structure()
        print(f"Directory Structure: {struct_result['status']}")
        
        # Import validation
        import_result = self.validate_imports()
        print(f"Import Integrity: {import_result['status']} ({import_result['passed']}/{import_result['total']} passed)")
        
        # Overall assessment
        all_tests = [root_result, struct_result, import_result]
        passed_tests = sum(1 for test in all_tests if test['status'] == 'PASS')
        overall_status = 'PASS' if passed_tests == len(all_tests) else 'PARTIAL' if passed_tests > 0 else 'FAIL'
        
        print(f"\nOVERALL QA STATUS: {overall_status} ({passed_tests}/{len(all_tests)} tests passed)")
        
        # Detailed results
        self.results.update({
            'root_directory': root_result,
            'directory_structure': struct_result,
            'import_integrity': import_result,
            'overall_status': overall_status,
            'tests_passed': passed_tests,
            'total_tests': len(all_tests)
        })
        
        # Save results
        report_file = self.root_dir / '.temp_reorganization_plan' / 'qa_validation_results.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results: {report_file}")
        
        return overall_status == 'PASS'

if __name__ == '__main__':
    validator = EnterpriseQAValidator()
    success = validator.run_full_validation()
    exit(0 if success else 1)