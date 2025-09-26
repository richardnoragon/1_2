#!/usr/bin/env python3
"""
Secure Delete Migration Validation Script

Comprehensive validation script to verify successful migration of secure_delete
functionality to file_utilities_2 package with full hub integration.

Validation Categories:
- Import validation
- Functionality validation  
- Hub integration validation
- Configuration validation
- UI validation
- Cleanup validation
"""

import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def test_imports() -> Dict[str, Any]:
    """Test all secure delete imports."""
    print_section("1. IMPORT VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'import_errors': []
    }
    
    # Test core imports
    print_subsection("Core Module Imports")
    try:
        from file_utilities_2.core.secure_delete_logic import SecureDeleteLogic
        from file_utilities_2.core.secure_delete_config import SecureDeleteConfig, get_config
        from file_utilities_2.core.secure_delete_logging import SecureDeleteLogger, get_logger
        print("✅ Core modules imported successfully")
        results['details']['core_imports'] = 'SUCCESS'
    except Exception as e:
        print(f"❌ Core import failed: {e}")
        results['status'] = 'FAIL'
        results['import_errors'].append(f"Core imports: {e}")
        results['details']['core_imports'] = 'FAILED'
    
    # Test GUI imports
    print_subsection("GUI Module Imports")
    try:
        from file_utilities_2.gui.secure_delete_gui import SecureDeleteGUI
        print("✅ GUI modules imported successfully")
        results['details']['gui_imports'] = 'SUCCESS'
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        results['status'] = 'FAIL'
        results['import_errors'].append(f"GUI imports: {e}")
        results['details']['gui_imports'] = 'FAILED'
    
    # Test integration imports
    print_subsection("Integration Module Imports")
    try:
        from file_utilities_2.integration.secure_delete_connector import SecureDeleteHubConnector
        print("✅ Integration modules imported successfully")
        results['details']['integration_imports'] = 'SUCCESS'
    except Exception as e:
        print(f"❌ Integration import failed: {e}")
        results['status'] = 'FAIL'
        results['import_errors'].append(f"Integration imports: {e}")
        results['details']['integration_imports'] = 'FAILED'
    
    # Test package-level imports
    print_subsection("Package-Level Imports")
    try:
        from file_utilities_2 import SecureDeleteLogic, SecureDeleteGUI, SecureDeleteConfig
        print("✅ Package-level imports successful")
        results['details']['package_imports'] = 'SUCCESS'
    except Exception as e:
        print(f"❌ Package-level import failed: {e}")
        results['status'] = 'FAIL'
        results['import_errors'].append(f"Package imports: {e}")
        results['details']['package_imports'] = 'FAILED'
    
    return results

def test_functionality() -> Dict[str, Any]:
    """Test core functionality."""
    print_section("2. FUNCTIONALITY VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'errors': []
    }
    
    try:
        from file_utilities_2.core.secure_delete_logic import SecureDeleteLogic
        from file_utilities_2.core.secure_delete_config import SecureDeleteConfig
        from file_utilities_2.core.secure_delete_logging import SecureDeleteLogger
        
        # Test logic initialization
        print_subsection("Core Logic Validation")
        logic = SecureDeleteLogic()
        print("✅ SecureDeleteLogic initialized")
        
        # Test configuration
        print_subsection("Configuration Validation")
        config = SecureDeleteConfig()
        default_passes = config.get_setting('default_passes')
        print(f"✅ Configuration loaded (default_passes: {default_passes})")
        
        # Test logging
        print_subsection("Logging Validation")
        logger = SecureDeleteLogger("ValidationTest")
        print("✅ Logging system initialized")
        
        # Test random generation
        print_subsection("Random Generation Validation")
        random_bytes = logic._generate_random_bytes(1024)
        random_filename = logic._generate_random_filename()
        print(f"✅ Random generation working (bytes: {len(random_bytes)}, filename: {random_filename})")
        
        results['details']['functionality'] = 'SUCCESS'
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        results['status'] = 'FAIL'
        results['errors'].append(str(e))
        results['details']['functionality'] = 'FAILED'
    
    return results

def test_hub_integration() -> Dict[str, Any]:
    """Test hub integration."""
    print_section("3. HUB INTEGRATION VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'errors': []
    }
    
    try:
        from file_utilities_2.integration.secure_delete_connector import SecureDeleteHubConnector
        
        # Test hub connector initialization
        print_subsection("Hub Connector Validation")
        connector = SecureDeleteHubConnector()
        print("✅ Hub connector initialized")
        
        # Test resource management
        print_subsection("Resource Management Validation")
        status = connector.get_connector_status()
        print(f"✅ Resource management active (allocated: {len(status['allocated_resources'])})")
        
        # Test performance metrics
        print_subsection("Performance Metrics Validation")
        metrics = connector.performance_metrics
        print(f"✅ Performance metrics tracking (ops: {metrics['operations_completed']})")
        
        results['details']['hub_integration'] = 'SUCCESS'
        
    except Exception as e:
        print(f"❌ Hub integration test failed: {e}")
        results['status'] = 'FAIL'
        results['errors'].append(str(e))
        results['details']['hub_integration'] = 'FAILED'
    
    return results

def test_gui_integration() -> Dict[str, Any]:
    """Test GUI integration."""
    print_section("4. GUI INTEGRATION VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'errors': []
    }
    
    try:
        # Test GUI imports without creating QApplication
        from file_utilities_2.gui.secure_delete_gui import SecureDeleteGUI
        print("✅ GUI class imported successfully")
        
        # Test UI file existence
        ui_file = Path("file_utilities_2/gui/secure_delete.ui")
        if ui_file.exists():
            print("✅ UI file exists in new location")
        else:
            print("❌ UI file missing in new location")
            results['status'] = 'FAIL'
            results['errors'].append("UI file not found")
        
        results['details']['gui_integration'] = 'SUCCESS'
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        results['status'] = 'FAIL'
        results['errors'].append(str(e))
        results['details']['gui_integration'] = 'FAILED'
    
    return results

def test_rfuhub_integration() -> Dict[str, Any]:
    """Test RFU Hub integration."""
    print_section("5. RFU HUB INTEGRATION VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'errors': []
    }
    
    try:
        # Check if rfuhub.py has been updated
        with open('rfuhub.py', 'r') as f:
            content = f.read()
        
        if 'file_utilities_2.gui.secure_delete_gui' in content:
            print("✅ RFU Hub import updated to new location")
        else:
            print("❌ RFU Hub still using old import")
            results['status'] = 'FAIL'
            results['errors'].append("RFU Hub import not updated")
        
        if 'SecureDeleteGUI(hub_instance=self)' in content:
            print("✅ RFU Hub using hub integration")
        else:
            print("❌ RFU Hub not using hub integration")
            results['status'] = 'FAIL'
            results['errors'].append("RFU Hub hub integration missing")
        
        results['details']['rfuhub_integration'] = 'SUCCESS'
        
    except Exception as e:
        print(f"❌ RFU Hub integration test failed: {e}")
        results['status'] = 'FAIL'
        results['errors'].append(str(e))
        results['details']['rfuhub_integration'] = 'FAILED'
    
    return results

def test_file_structure() -> Dict[str, Any]:
    """Test file structure."""
    print_section("6. FILE STRUCTURE VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'missing_files': []
    }
    
    expected_files = [
        'file_utilities_2/core/secure_delete_logic.py',
        'file_utilities_2/core/secure_delete_config.py',
        'file_utilities_2/core/secure_delete_logging.py',
        'file_utilities_2/gui/secure_delete_gui.py',
        'file_utilities_2/gui/secure_delete.ui',
        'file_utilities_2/integration/secure_delete_connector.py',
        'file_utilities_2/tests/test_secure_delete.py'
    ]
    
    print_subsection("Required Files Check")
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            results['status'] = 'FAIL'
            results['missing_files'].append(file_path)
    
    # Check backup files
    print_subsection("Backup Files Check")
    backup_dir = Path("backup/secure_delete_migration")
    if backup_dir.exists():
        backup_folders = list(backup_dir.glob("*"))
        if backup_folders:
            latest_backup = max(backup_folders, key=lambda p: p.stat().st_mtime)
            print(f"✅ Backup exists: {latest_backup}")
            
            # Check backup contents
            backup_files = ['secure_delete.py', 'secure_delete.ui', 'backup_manifest.txt']
            for backup_file in backup_files:
                if (latest_backup / backup_file).exists():
                    print(f"✅ Backup contains: {backup_file}")
                else:
                    print(f"❌ Backup missing: {backup_file}")
        else:
            print("❌ No backup folders found")
            results['status'] = 'FAIL'
    else:
        print("❌ Backup directory not found")
        results['status'] = 'FAIL'
    
    results['details']['file_structure'] = 'SUCCESS' if results['status'] == 'PASS' else 'FAILED'
    return results

def test_cleanup_status() -> Dict[str, Any]:
    """Test cleanup status."""
    print_section("7. CLEANUP STATUS VALIDATION")
    
    results = {
        'status': 'PASS',
        'details': {},
        'remaining_files': []
    }
    
    # Check if original files still exist
    original_files = ['secure_delete.py', 'secure_delete.ui']
    
    print_subsection("Original Files Status")
    for file_path in original_files:
        if os.path.exists(file_path):
            print(f"⚠️  {file_path} - STILL EXISTS (ready for cleanup)")
            results['remaining_files'].append(file_path)
        else:
            print(f"✅ {file_path} - CLEANED UP")
    
    if results['remaining_files']:
        results['details']['cleanup_needed'] = True
        print("\n📋 Files ready for cleanup:")
        for file_path in results['remaining_files']:
            print(f"   - {file_path}")
    else:
        results['details']['cleanup_needed'] = False
        print("✅ All original files have been cleaned up")
    
    results['details']['cleanup_status'] = 'PENDING' if results['remaining_files'] else 'COMPLETE'
    return results

def generate_validation_report(all_results: Dict[str, Dict[str, Any]]) -> str:
    """Generate comprehensive validation report."""
    print_section("8. VALIDATION SUMMARY REPORT")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for result in all_results.values() if result['status'] == 'PASS')
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, result in all_results.items():
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"   {status_icon} {test_name}: {result['status']}")
        
        if result['status'] == 'FAIL':
            if 'import_errors' in result and result['import_errors']:
                for error in result['import_errors']:
                    print(f"      - Import Error: {error}")
            if 'errors' in result and result['errors']:
                for error in result['errors']:
                    print(f"      - Error: {error}")
            if 'missing_files' in result and result['missing_files']:
                for file_path in result['missing_files']:
                    print(f"      - Missing: {file_path}")
    
    # Overall status
    overall_status = "PASS" if passed_tests == total_tests else "FAIL"
    print(f"\n🎯 OVERALL MIGRATION STATUS: {overall_status}")
    
    if overall_status == "PASS":
        print("🎉 Secure Delete migration completed successfully!")
        print("   All functionality has been migrated to file_utilities_2")
        print("   Hub integration is active and functional")
        print("   Ready for production use")
    else:
        print("⚠️  Migration validation found issues that need attention")
        print("   Please review the failed tests above")
        print("   Fix any issues before proceeding with cleanup")
    
    return overall_status

def main():
    """Run comprehensive validation."""
    print("🔍 SECURE DELETE MIGRATION VALIDATION")
    print("=====================================")
    print("Validating migration of secure_delete functionality")
    print("to file_utilities_2 package with hub integration")
    
    # Run all validation tests
    all_results = {}
    
    try:
        all_results['Import Tests'] = test_imports()
        all_results['Functionality Tests'] = test_functionality()
        all_results['Hub Integration Tests'] = test_hub_integration()
        all_results['GUI Integration Tests'] = test_gui_integration()
        all_results['RFU Hub Integration Tests'] = test_rfuhub_integration()
        all_results['File Structure Tests'] = test_file_structure()
        all_results['Cleanup Status Tests'] = test_cleanup_status()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during validation: {e}")
        traceback.print_exc()
        return False
    
    # Generate final report
    overall_status = generate_validation_report(all_results)
    
    return overall_status == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)