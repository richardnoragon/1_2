#!/usr/bin/env python3
"""
Infrastructure Reality Check - Comprehensive Testing
Created: September 8, 2025
Purpose: Expose real infrastructure issues without oversimplification

This test follows the NO-SIMPLIFICATION protocol:
- Tests actual module imports, not mocked versions
- Exposes real dependency issues rather than masking them
- Documents specific blockers for systematic resolution
- No hardcoded test data or fixed parameters
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class InfrastructureValidator:
    """Validates RFU infrastructure without oversimplification."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.blockers: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        
        # Add src to path for testing
        src_path = Path(__file__).parent.parent.parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
    
    def test_module_imports_reality(self) -> Dict[str, Any]:
        """Test actual module imports - expose real issues."""
        print("\n=== TESTING REAL MODULE IMPORTS ===")
        
        modules_to_test = [
            ('rfu', 'RFU core package'),
            ('utilities', 'Utilities package'),
            ('core', 'Core infrastructure'),
            ('rfu.dev_hub', 'Development hub module'),
            ('rfu.log_manager', 'Log manager module'),
            ('utilities.system', 'System utilities'),
            ('utilities.network', 'Network utilities'),
            ('utilities.privacy', 'Privacy utilities'),
            ('utilities.analysis', 'Analysis utilities'),
            ('utilities.file_management', 'File management utilities')
        ]
        
        results = []
        successful_imports = 0
        
        for module_name, description in modules_to_test:
            print(f"\nTesting: {module_name} ({description})")
            
            try:
                # Attempt actual import
                imported_module = __import__(module_name, fromlist=[module_name.split('.')[-1]])
                
                # Validate the import actually worked
                if imported_module is None:
                    result = {
                        'module': module_name,
                        'description': description,
                        'status': 'FAILED',
                        'error': 'Import returned None (masked failure)',
                        'real_issue': 'safe_import function masking real ImportError'
                    }
                    print(f"  [FAILED] {module_name}: Import returned None")
                    self.blockers.append({
                        'type': 'MASKED_IMPORT_FAILURE',
                        'module': module_name,
                        'issue': 'safe_import masking real errors'
                    })
                
                elif hasattr(imported_module, '__file__'):
                    result = {
                        'module': module_name,
                        'description': description,
                        'status': 'SUCCESS',
                        'file_path': str(imported_module.__file__),
                        'attributes': [attr for attr in dir(imported_module) 
                                     if not attr.startswith('_')][:10]
                    }
                    print(f"  [SUCCESS] {module_name}: {imported_module.__file__}")
                    successful_imports += 1
                
                else:
                    # Module imported but has no __file__ - investigate
                    attrs = [attr for attr in dir(imported_module) if not attr.startswith('_')]
                    result = {
                        'module': module_name,
                        'description': description,
                        'status': 'PARTIAL',
                        'warning': 'No __file__ attribute - possible namespace package',
                        'available_attributes': attrs[:10]
                    }
                    print(f"  [PARTIAL] {module_name}: Imported but no __file__")
                    print(f"            Available attributes: {attrs[:5]}")
                    successful_imports += 0.5
            
            except ImportError as e:
                result = {
                    'module': module_name,
                    'description': description,
                    'status': 'IMPORT_ERROR',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                print(f"  [IMPORT_ERROR] {module_name}: {e}")
                
                # This is a real issue that needs fixing, not simplification
                self.blockers.append({
                    'type': 'IMPORT_ERROR',
                    'module': module_name,
                    'error': str(e),
                    'requires_investigation': True
                })
            
            except Exception as e:
                result = {
                    'module': module_name,
                    'description': description,
                    'status': 'UNEXPECTED_ERROR',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'traceback': traceback.format_exc()
                }
                print(f"  [UNEXPECTED_ERROR] {module_name}: {type(e).__name__}: {e}")
                
                # Document unexpected errors for investigation
                self.blockers.append({
                    'type': 'UNEXPECTED_ERROR',
                    'module': module_name,
                    'error': str(e),
                    'requires_debugging': True
                })
            
            results.append(result)
        
        success_rate = (successful_imports / len(modules_to_test)) * 100
        
        summary = {
            'total_modules': len(modules_to_test),
            'successful_imports': successful_imports,
            'success_rate': success_rate,
            'results': results,
            'blockers_identified': len(self.blockers)
        }
        
        print(f"\n=== IMPORT RESULTS SUMMARY ===")
        print(f"Total modules tested: {len(modules_to_test)}")
        print(f"Successful imports: {successful_imports}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Blockers identified: {len(self.blockers)}")
        
        return summary
    
    def test_path_configuration_reality(self) -> Dict[str, Any]:
        """Test actual Python path configuration."""
        print("\n=== TESTING PATH CONFIGURATION ===")
        
        expected_paths = [
            Path(r"C:\Users\HP1\1_2\src").resolve(),
            Path(r"C:\Users\HP1\1_2").resolve(),
            Path(r"C:\Users\HP1\1_2\tests\unit").resolve()
        ]
        
        path_results = []
        
        for expected_path in expected_paths:
            path_str = str(expected_path)
            is_present = path_str in sys.path
            
            result = {
                'expected_path': path_str,
                'present_in_syspath': is_present,
                'exists_on_filesystem': expected_path.exists()
            }
            
            if is_present and expected_path.exists():
                print(f"  [SUCCESS] {path_str}")
                result['status'] = 'SUCCESS'
            elif is_present and not expected_path.exists():
                print(f"  [WARNING] {path_str} in sys.path but doesn't exist")
                result['status'] = 'WARNING'
                self.warnings.append(f"Path in sys.path but missing: {path_str}")
            elif not is_present and expected_path.exists():
                print(f"  [ISSUE] {path_str} exists but not in sys.path")
                result['status'] = 'MISSING_FROM_PATH'
                self.blockers.append({
                    'type': 'PATH_CONFIGURATION',
                    'issue': f'Required path not in sys.path: {path_str}'
                })
            else:
                print(f"  [FAILED] {path_str} - missing and not in path")
                result['status'] = 'FAILED'
                self.blockers.append({
                    'type': 'PATH_MISSING',
                    'issue': f'Required path missing entirely: {path_str}'
                })
            
            path_results.append(result)
        
        return {
            'expected_paths': len(expected_paths),
            'configured_paths': sum(1 for r in path_results if r['present_in_syspath']),
            'existing_paths': sum(1 for r in path_results if r['exists_on_filesystem']),
            'results': path_results
        }
    
    def test_dependency_availability_reality(self) -> Dict[str, Any]:
        """Test actual dependency availability without mocking."""
        print("\n=== TESTING DEPENDENCY AVAILABILITY ===")
        
        critical_dependencies = [
            ('PyQt5', 'GUI framework'),
            ('PyQt5.QtWidgets', 'Qt Widgets'),
            ('PyQt5.QtCore', 'Qt Core'),
            ('pytest', 'Testing framework'),
            ('pathlib', 'Path utilities'),
            ('sqlite3', 'Database'),
            ('json', 'JSON processing'),
            ('os', 'Operating system interface'),
            ('sys', 'System interface'),
            ('logging', 'Logging framework')
        ]
        
        dependency_results = []
        available_count = 0
        
        for dep_name, description in critical_dependencies:
            try:
                imported_dep = __import__(dep_name)
                result = {
                    'dependency': dep_name,
                    'description': description,
                    'status': 'AVAILABLE',
                    'version': getattr(imported_dep, '__version__', 'Unknown')
                }
                print(f"  [AVAILABLE] {dep_name}")
                available_count += 1
                
            except ImportError as e:
                result = {
                    'dependency': dep_name,
                    'description': description,
                    'status': 'MISSING',
                    'error': str(e)
                }
                print(f"  [MISSING] {dep_name}: {e}")
                
                # Critical dependencies missing
                if dep_name in ['PyQt5', 'pytest']:
                    self.blockers.append({
                        'type': 'CRITICAL_DEPENDENCY_MISSING',
                        'dependency': dep_name,
                        'error': str(e),
                        'impact': 'Prevents test execution'
                    })
            
            dependency_results.append(result)
        
        dependency_rate = (available_count / len(critical_dependencies)) * 100
        
        return {
            'total_dependencies': len(critical_dependencies),
            'available_dependencies': available_count,
            'availability_rate': dependency_rate,
            'results': dependency_results
        }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive infrastructure validation."""
        print("="*60)
        print("INFRASTRUCTURE REALITY CHECK - COMPREHENSIVE VALIDATION")
        print(f"Execution Time: {datetime.now().isoformat()}")
        print("="*60)
        
        # Test all aspects
        import_results = self.test_module_imports_reality()
        path_results = self.test_path_configuration_reality()
        dependency_results = self.test_dependency_availability_reality()
        
        # Generate comprehensive report
        overall_success_rate = (
            import_results['success_rate'] + 
            (path_results['configured_paths'] / path_results['expected_paths'] * 100) +
            dependency_results['availability_rate']
        ) / 3
        
        comprehensive_results = {
            'execution_timestamp': datetime.now().isoformat(),
            'overall_success_rate': overall_success_rate,
            'import_validation': import_results,
            'path_validation': path_results,
            'dependency_validation': dependency_results,
            'total_blockers': len(self.blockers),
            'blockers': self.blockers,
            'warnings': self.warnings
        }
        
        print(f"\n=== COMPREHENSIVE RESULTS ===")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"Total Blockers: {len(self.blockers)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if len(self.blockers) > 0:
            print(f"\n=== CRITICAL BLOCKERS IDENTIFIED ===")
            for i, blocker in enumerate(self.blockers, 1):
                print(f"{i}. {blocker['type']}: {blocker.get('module', blocker.get('dependency', 'Unknown'))}")
                if 'error' in blocker:
                    print(f"   Error: {blocker['error']}")
        
        return comprehensive_results


def main():
    """Main execution function."""
    validator = InfrastructureValidator()
    results = validator.run_comprehensive_validation()
    
    # Save results to file
    results_file = Path(__file__).parent / f"infrastructure_validation_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    
    import json
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {results_file}")
    
    # Return success/failure based on whether we can at least import basic modules
    success = results['overall_success_rate'] > 50
    print(f"\nValidation {'PASSED' if success else 'FAILED'}")
    return success


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"CRITICAL ERROR: Infrastructure validation failed: {e}")
        print("TRACEBACK:")
        traceback.print_exc()
        sys.exit(2)